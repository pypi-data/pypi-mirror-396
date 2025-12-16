"""
ThalosForge Optimization Suite
==============================

pip install thalosforge

Usage:
    import thalosforge as tf
    
    tf.configure(api_key="tf_...")  # Required
    
    result = tf.optimize(
        func="sum(x**2)",  # Expression string
        bounds=[(-5, 5)] * 10
    )
    print(result.objective)

Get your API key at https://www.thalosforge.com/pricing
"""

__version__ = "1.0.1"
__author__ = "ThalosForge Inc."

import os
import json
import time
from typing import Optional, List, Tuple, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False


# =============================================================================
# RESULT TYPES
# =============================================================================

class Status(Enum):
    OPTIMAL = "optimal"
    SUCCESS = "success"
    FEASIBLE = "feasible"
    INFEASIBLE = "infeasible"
    TIMEOUT = "timeout"
    ERROR = "error"


@dataclass
class Result:
    """Optimization result."""
    status: Status
    objective: float
    x: List[float]
    iterations: int = 0
    evaluations: int = 0
    time: float = 0.0
    engine: str = ""
    optimization_id: str = ""
    
    def __repr__(self):
        return f"Result(status={self.status.value}, objective={self.objective:.6e}, evaluations={self.evaluations})"
    
    def to_dict(self) -> Dict:
        return {
            "status": self.status.value,
            "objective": self.objective,
            "x": self.x,
            "iterations": self.iterations,
            "evaluations": self.evaluations,
            "time": self.time,
            "engine": self.engine,
            "optimization_id": self.optimization_id,
        }
    
    def to_json(self, path: str = None) -> str:
        data = json.dumps(self.to_dict(), indent=2)
        if path:
            with open(path, 'w') as f:
                f.write(data)
        return data


# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    """ThalosForge configuration."""
    
    def __init__(
        self,
        api_key: str = None,
        base_url: str = "https://api.thalosforge.com",
        timeout: float = 300.0,
        max_retries: int = 3,
    ):
        self.api_key = api_key or os.environ.get("THALOSFORGE_API_KEY", "")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
    
    @classmethod
    def from_env(cls):
        """Create configuration from environment variables."""
        return cls(
            api_key=os.environ.get("THALOSFORGE_API_KEY"),
            base_url=os.environ.get("THALOSFORGE_BASE_URL", "https://api.thalosforge.com"),
            timeout=float(os.environ.get("THALOSFORGE_TIMEOUT", "300")),
        )


# Global configuration
_config: Optional[Config] = None


def configure(
    api_key: str = None,
    base_url: str = None,
    timeout: float = None,
    **kwargs
):
    """
    Configure ThalosForge globally.
    
    Parameters
    ----------
    api_key : str
        Your ThalosForge API key (required). Get one at https://www.thalosforge.com/pricing
    base_url : str, optional
        API base URL (default: https://api.thalosforge.com)
    timeout : float, optional
        Request timeout in seconds (default: 300)
    
    Examples
    --------
    >>> import thalosforge as tf
    >>> tf.configure(api_key="tf_...")
    """
    global _config
    
    current = _config or Config()
    
    _config = Config(
        api_key=api_key or current.api_key,
        base_url=base_url or current.base_url,
        timeout=timeout or current.timeout,
    )


def _get_config() -> Config:
    """Get current configuration, initializing from env if needed."""
    global _config
    if _config is None:
        _config = Config.from_env()
    return _config


# =============================================================================
# API CLIENT
# =============================================================================

class APIError(Exception):
    """ThalosForge API error."""
    def __init__(self, message: str, status_code: int = None, detail: Any = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(message)


class Client:
    """ThalosForge API client."""
    
    def __init__(self, config: Config = None):
        self.config = config or _get_config()
        
        if not self.config.api_key:
            raise APIError(
                "API key required. Get one at https://www.thalosforge.com/pricing\n"
                "Then: tf.configure(api_key='tf_...')\n"
                "Or set THALOSFORGE_API_KEY environment variable."
            )
    
    def _request(self, method: str, endpoint: str, data: Dict = None) -> Dict:
        """Make API request."""
        url = f"{self.config.base_url}{endpoint}"
        headers = {
            "X-API-Key": self.config.api_key,
            "Content-Type": "application/json",
            "User-Agent": f"thalosforge-python/{__version__}",
        }
        
        # Try httpx first, then requests
        if HTTPX_AVAILABLE:
            return self._request_httpx(method, url, headers, data)
        elif REQUESTS_AVAILABLE:
            return self._request_requests(method, url, headers, data)
        else:
            raise APIError(
                "No HTTP library available. Install one:\n"
                "  pip install thalosforge[cloud]"
            )
    
    def _request_httpx(self, method: str, url: str, headers: Dict, data: Dict) -> Dict:
        """Make request using httpx."""
        import httpx
        
        try:
            with httpx.Client(timeout=self.config.timeout) as client:
                if method == "GET":
                    response = client.get(url, headers=headers)
                else:
                    response = client.post(url, headers=headers, json=data)
                
                if response.status_code == 401:
                    raise APIError("Invalid API key", status_code=401)
                elif response.status_code == 402:
                    raise APIError("Quota exceeded. Upgrade at https://www.thalosforge.com/pricing", status_code=402)
                elif response.status_code == 403:
                    detail = response.json().get("detail", {})
                    raise APIError(f"Access denied: {detail}", status_code=403, detail=detail)
                elif response.status_code >= 400:
                    detail = response.json().get("detail", response.text)
                    raise APIError(f"API error: {detail}", status_code=response.status_code)
                
                return response.json()
                
        except httpx.TimeoutException:
            raise APIError("Request timeout")
        except httpx.RequestError as e:
            raise APIError(f"Request failed: {e}")
    
    def _request_requests(self, method: str, url: str, headers: Dict, data: Dict) -> Dict:
        """Make request using requests."""
        import requests
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=self.config.timeout)
            else:
                response = requests.post(url, headers=headers, json=data, timeout=self.config.timeout)
            
            if response.status_code == 401:
                raise APIError("Invalid API key", status_code=401)
            elif response.status_code == 402:
                raise APIError("Quota exceeded. Upgrade at https://www.thalosforge.com/pricing", status_code=402)
            elif response.status_code == 403:
                detail = response.json().get("detail", {})
                raise APIError(f"Access denied: {detail}", status_code=403, detail=detail)
            elif response.status_code >= 400:
                detail = response.json().get("detail", response.text)
                raise APIError(f"API error: {detail}", status_code=response.status_code)
            
            return response.json()
            
        except requests.exceptions.Timeout:
            raise APIError("Request timeout")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {e}")
    
    def health(self) -> Dict:
        """Check API health."""
        return self._request("GET", "/health")
    
    def usage(self) -> Dict:
        """Get usage statistics."""
        return self._request("GET", "/v1/usage")
    
    def engines(self) -> Dict:
        """List available engines."""
        return self._request("GET", "/v1/engines")
    
    def optimize(
        self,
        bounds: List[Tuple[float, float]],
        objective_expression: str,
        engine: str = "auto",
        max_evaluations: int = 1000,
        deterministic: bool = False,
        constraints: List[Dict] = None,
    ) -> Result:
        """
        Run optimization via API.
        
        Parameters
        ----------
        bounds : list of tuples
            Variable bounds [(lb, ub), ...]
        objective_expression : str
            Math expression like 'sum(x**2)' or '10*n + sum(x**2 - 10*cos(2*pi*x))'
        engine : str
            Engine: 'auto', 'quantumjolt', 'dss', 'kestrel'
        max_evaluations : int
            Maximum function evaluations
        deterministic : bool
            Force deterministic DSS engine
        constraints : list of dict, optional
            Constraints for Kestrel engine
        
        Returns
        -------
        Result
            Optimization result
        """
        data = {
            "bounds": [list(b) for b in bounds],
            "objective_expression": objective_expression,
            "engine": engine,
            "max_evaluations": max_evaluations,
            "deterministic": deterministic,
        }
        
        if constraints:
            data["constraints"] = constraints
        
        response = self._request("POST", "/v1/optimize", data)
        
        return Result(
            status=Status(response.get("status", "success")),
            objective=response["best_value"],
            x=response["best_point"],
            iterations=response.get("iterations", 0),
            evaluations=response["evaluations"],
            time=response["time_seconds"],
            engine=response["engine_used"],
            optimization_id=response["optimization_id"],
        )


# =============================================================================
# MAIN API
# =============================================================================

def optimize(
    func: str,
    bounds: Union[List[Tuple[float, float]], List[List[float]]],
    engine: str = "auto",
    max_evaluations: int = 1000,
    deterministic: bool = False,
    constraints: List[Dict] = None,
    verbose: bool = False,
) -> Result:
    """
    Optimize a function via ThalosForge API.
    
    Parameters
    ----------
    func : str
        Objective function as math expression. Available:
        - Variables: x (array), n (dimensions)
        - Functions: sum, prod, mean, abs, sqrt, exp, log, sin, cos, tan
        - Constants: pi, e
        
        Examples:
        - "sum(x**2)"
        - "10*n + sum(x**2 - 10*cos(2*pi*x))"  # Rastrigin
        - "sum(100*(x[1:]-x[:-1]**2)**2 + (1-x[:-1])**2)"  # Rosenbrock
        
    bounds : list of tuples
        Variable bounds [(lower, upper), ...]
    engine : str
        Optimization engine:
        - "auto": Auto-select based on problem
        - "quantumjolt": High-dimensional SPSA (100+ dims)
        - "dss": Deterministic spiral search
        - "kestrel": Constrained optimization
    max_evaluations : int
        Maximum function evaluations (default: 1000)
    deterministic : bool
        Force deterministic mode (default: False)
    constraints : list of dict, optional
        Constraints for Kestrel: [{"expression": "x[0] + x[1]", "type": "leq", "rhs": 10}]
    verbose : bool
        Print progress (default: False)
    
    Returns
    -------
    Result
        Optimization result with status, objective, x, etc.
    
    Examples
    --------
    >>> import thalosforge as tf
    >>> tf.configure(api_key="tf_...")
    >>> 
    >>> result = tf.optimize(
    ...     func="sum(x**2)",
    ...     bounds=[(-5, 5)] * 10
    ... )
    >>> print(result.objective)
    0.0
    
    >>> # Constrained optimization
    >>> result = tf.optimize(
    ...     func="x[0] + x[1]",
    ...     bounds=[(0, 10), (0, 10)],
    ...     engine="kestrel",
    ...     constraints=[{"expression": "x[0] + x[1]", "type": "leq", "rhs": 15}]
    ... )
    """
    client = Client()
    
    if verbose:
        print(f"ThalosForge: Optimizing with {engine.upper()} engine")
        print(f"  Dimensions: {len(bounds)}")
        print(f"  Max evaluations: {max_evaluations}")
    
    result = client.optimize(
        bounds=bounds,
        objective_expression=func,
        engine=engine,
        max_evaluations=max_evaluations,
        deterministic=deterministic,
        constraints=constraints,
    )
    
    if verbose:
        print(f"  Status: {result.status.value}")
        print(f"  Objective: {result.objective:.6e}")
        print(f"  Time: {result.time:.2f}s")
    
    return result


def minimize(func: str, bounds, **kwargs) -> Result:
    """Alias for optimize()."""
    return optimize(func, bounds, **kwargs)


def maximize(func: str, bounds, **kwargs) -> Result:
    """Maximize a function (negates objective internally)."""
    # API handles this by negating
    result = optimize(f"-({func})", bounds, **kwargs)
    result.objective = -result.objective
    return result


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def usage() -> Dict:
    """Get your current API usage."""
    return Client().usage()


def engines() -> List[Dict]:
    """List available optimization engines."""
    return Client().engines()["engines"]


def health() -> Dict:
    """Check API health."""
    return Client().health()


# =============================================================================
# CLI
# =============================================================================

def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="ThalosForge Optimization Suite")
    parser.add_argument("--version", action="store_true", help="Show version")
    parser.add_argument("--health", action="store_true", help="Check API health")
    parser.add_argument("--usage", action="store_true", help="Show usage stats")
    parser.add_argument("--engines", action="store_true", help="List engines")
    
    args = parser.parse_args()
    
    if args.version:
        print(f"ThalosForge v{__version__}")
        return
    
    if args.health:
        try:
            h = health()
            print(f"Status: {h.get('status', 'unknown')}")
            print(f"Version: {h.get('version', 'unknown')}")
        except APIError as e:
            print(f"Error: {e.message}")
        return
    
    if args.usage:
        try:
            u = usage()
            print(f"Tier: {u.get('tier', 'unknown')}")
            print(f"Used: {u.get('optimizations_used', 0)}/{u.get('optimizations_limit', '?')}")
        except APIError as e:
            print(f"Error: {e.message}")
        return
    
    if args.engines:
        try:
            for e in engines():
                print(f"  {e['id']:15s} - {e['description']}")
        except APIError as e:
            print(f"Error: {e.message}")
        return
    
    # Default: show help
    print("ThalosForge Optimization Suite")
    print("=" * 40)
    print(f"Version: {__version__}")
    print()
    print("Usage:")
    print("  import thalosforge as tf")
    print("  tf.configure(api_key='tf_...')")
    print("  result = tf.optimize('sum(x**2)', [(-5,5)]*10)")
    print()
    print("Get your API key at https://www.thalosforge.com/pricing")


if __name__ == "__main__":
    main()
