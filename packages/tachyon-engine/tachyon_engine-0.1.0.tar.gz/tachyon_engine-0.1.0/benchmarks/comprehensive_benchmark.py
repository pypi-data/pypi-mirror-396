"""
Comprehensive benchmark comparing Tachyon Engine vs Starlette
"""

import time
import asyncio
import statistics
from typing import List, Dict, Any
import json

try:
    from tachyon_engine import (
        TachyonEngine, 
        Route, 
        Request, 
        JSONResponse,
        Headers,
        QueryParams,
    )
    TACHYON_AVAILABLE = True
except ImportError:
    TACHYON_AVAILABLE = False
    print("⚠️  Tachyon Engine not available. Run: maturin develop")
    print("   Skipping Tachyon benchmarks\n")

from starlette.applications import Starlette
from starlette.routing import Route as StarletteRoute
from starlette.responses import JSONResponse as StarletteJSONResponse
from starlette.requests import Request as StarletteRequest


class BenchmarkResults:
    """Store and display benchmark results"""
    
    def __init__(self):
        self.results: Dict[str, Dict[str, Any]] = {}
    
    def add_result(self, test_name: str, framework: str, times: List[float]):
        if test_name not in self.results:
            self.results[test_name] = {}
        
        self.results[test_name][framework] = {
            'mean': statistics.mean(times),
            'median': statistics.median(times),
            'stdev': statistics.stdev(times) if len(times) > 1 else 0,
            'min': min(times),
            'max': max(times),
            'total': sum(times),
            'iterations': len(times),
        }
    
    def calculate_speedup(self, test_name: str) -> float:
        if test_name not in self.results:
            return 0.0
        if 'Starlette' not in self.results[test_name]:
            return 0.0
        if 'Tachyon' not in self.results[test_name]:
            return 0.0
        
        starlette_time = self.results[test_name]['Starlette']['mean']
        tachyon_time = self.results[test_name]['Tachyon']['mean']
        
        if tachyon_time == 0:
            return 0.0
        
        return starlette_time / tachyon_time
    
    def print_results(self):
        print("\n" + "="*80)
        print("📊 BENCHMARK RESULTS")
        print("="*80)
        
        for test_name, frameworks in self.results.items():
            print(f"\n🔹 {test_name}")
            print("-" * 80)
            
            for framework, metrics in frameworks.items():
                print(f"\n  {framework}:")
                print(f"    Mean:       {metrics['mean']*1000:.4f} ms")
                print(f"    Median:     {metrics['median']*1000:.4f} ms")
                print(f"    Std Dev:    {metrics['stdev']*1000:.4f} ms")
                print(f"    Min:        {metrics['min']*1000:.4f} ms")
                print(f"    Max:        {metrics['max']*1000:.4f} ms")
                print(f"    Throughput: {metrics['iterations']/metrics['total']:.0f} ops/sec")
            
            speedup = self.calculate_speedup(test_name)
            if speedup > 0:
                emoji = "🚀" if speedup > 1 else "🐌"
                print(f"\n  {emoji} Speedup: {speedup:.2f}x {'faster' if speedup > 1 else 'slower'}")
        
        print("\n" + "="*80)


def benchmark_function(func, iterations=10000, warmup=100):
    """Benchmark a function with warmup"""
    # Warmup
    for _ in range(warmup):
        func()
    
    # Actual benchmark
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        times.append(end - start)
    
    return times


def test_app_creation(results: BenchmarkResults, iterations=1000):
    """Benchmark application creation"""
    print("\n🧪 Testing: Application Creation...")
    
    # Starlette
    def create_starlette():
        return Starlette(debug=False)
    
    times = benchmark_function(create_starlette, iterations=iterations, warmup=10)
    results.add_result("Application Creation", "Starlette", times)
    print(f"  ✓ Starlette: {len(times)} iterations")
    
    if TACHYON_AVAILABLE:
        # Tachyon
        def create_tachyon():
            return TachyonEngine(debug=False)
        
        times = benchmark_function(create_tachyon, iterations=iterations, warmup=10)
        results.add_result("Application Creation", "Tachyon", times)
        print(f"  ✓ Tachyon:   {len(times)} iterations")


def test_route_creation(results: BenchmarkResults, iterations=10000):
    """Benchmark route creation"""
    print("\n🧪 Testing: Route Creation...")
    
    # Starlette
    def create_starlette_route():
        async def handler(request):
            return StarletteJSONResponse({"status": "ok"})
        return StarletteRoute("/test", handler)
    
    times = benchmark_function(create_starlette_route, iterations=iterations)
    results.add_result("Route Creation", "Starlette", times)
    print(f"  ✓ Starlette: {len(times)} iterations")
    
    if TACHYON_AVAILABLE:
        # Tachyon
        def create_tachyon_route():
            async def handler(request):
                return JSONResponse({"status": "ok"})
            return Route("/test", handler, methods=["GET"])
        
        times = benchmark_function(create_tachyon_route, iterations=iterations)
        results.add_result("Route Creation", "Tachyon", times)
        print(f"  ✓ Tachyon:   {len(times)} iterations")


def test_json_response_creation(results: BenchmarkResults, iterations=10000):
    """Benchmark JSON response creation"""
    print("\n🧪 Testing: JSON Response Creation...")
    
    test_data = {
        "id": 12345,
        "name": "Test User",
        "email": "test@example.com",
        "active": True,
        "age": 30,
        "roles": ["user", "admin", "moderator"],
        "metadata": {
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-02T00:00:00Z",
            "login_count": 42,
            "preferences": {
                "theme": "dark",
                "notifications": True,
            }
        },
        "tags": ["python", "rust", "javascript", "go"],
    }
    
    # Starlette
    def create_starlette_response():
        return StarletteJSONResponse(test_data)
    
    times = benchmark_function(create_starlette_response, iterations=iterations)
    results.add_result("JSON Response Creation", "Starlette", times)
    print(f"  ✓ Starlette: {len(times)} iterations")
    
    if TACHYON_AVAILABLE:
        # Tachyon
        def create_tachyon_response():
            return JSONResponse(test_data)
        
        times = benchmark_function(create_tachyon_response, iterations=iterations)
        results.add_result("JSON Response Creation", "Tachyon", times)
        print(f"  ✓ Tachyon:   {len(times)} iterations")


def test_route_addition(results: BenchmarkResults, iterations=1000):
    """Benchmark adding routes to app"""
    print("\n🧪 Testing: Route Addition to App...")
    
    # Starlette
    def add_starlette_routes():
        app = Starlette(debug=False)
        async def handler(request):
            return StarletteJSONResponse({"ok": True})
        
        for i in range(10):
            route = StarletteRoute(f"/route_{i}", handler)
            app.routes.append(route)
        return app
    
    times = benchmark_function(add_starlette_routes, iterations=iterations, warmup=10)
    results.add_result("Adding 10 Routes", "Starlette", times)
    print(f"  ✓ Starlette: {len(times)} iterations")
    
    if TACHYON_AVAILABLE:
        # Tachyon
        def add_tachyon_routes():
            app = TachyonEngine(debug=False)
            async def handler(request):
                return JSONResponse({"ok": True})
            
            for i in range(10):
                route = Route(f"/route_{i}", handler, methods=["GET"])
                app.add_route(route)
            return app
        
        times = benchmark_function(add_tachyon_routes, iterations=iterations, warmup=10)
        results.add_result("Adding 10 Routes", "Tachyon", times)
        print(f"  ✓ Tachyon:   {len(times)} iterations")


def test_data_structure_operations(results: BenchmarkResults, iterations=50000):
    """Benchmark data structure operations"""
    
    if not TACHYON_AVAILABLE:
        return
    
    print("\n🧪 Testing: Data Structure Operations...")
    
    # Headers operations
    def headers_ops():
        headers = Headers()
        headers.set("Content-Type", "application/json")
        headers.set("Authorization", "Bearer token123")
        headers.set("X-Custom-Header", "value")
        _ = headers.get("content-type")
        _ = headers.contains("authorization")
    
    times = benchmark_function(headers_ops, iterations=iterations)
    results.add_result("Headers Operations", "Tachyon", times)
    print(f"  ✓ Headers:   {len(times)} iterations")
    
    # QueryParams operations (stub for now)
    def query_params_ops():
        params = QueryParams()
        # Operations would go here
    
    times = benchmark_function(query_params_ops, iterations=iterations)
    results.add_result("QueryParams Operations", "Tachyon", times)
    print(f"  ✓ QueryParams: {len(times)} iterations")


def save_results(results: BenchmarkResults, filename="benchmarks/results/latest.json"):
    """Save results to JSON file"""
    import os
    os.makedirs("benchmarks/results", exist_ok=True)
    
    output = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tachyon_available": TACHYON_AVAILABLE,
        "tests": results.results,
    }
    
    with open(filename, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\n💾 Results saved to: {filename}")


def print_summary(results: BenchmarkResults):
    """Print overall summary"""
    print("\n" + "="*80)
    print("📈 SUMMARY")
    print("="*80)
    
    if not TACHYON_AVAILABLE:
        print("\n❌ Tachyon Engine not available - cannot compare performance")
        print("   Run 'maturin develop' to build and test Tachyon")
        return
    
    speedups = []
    for test_name in results.results.keys():
        speedup = results.calculate_speedup(test_name)
        if speedup > 0:
            speedups.append((test_name, speedup))
    
    if speedups:
        print("\n🏆 Performance Comparison:")
        for test_name, speedup in sorted(speedups, key=lambda x: x[1], reverse=True):
            emoji = "🚀" if speedup > 1 else "🐌"
            status = "faster" if speedup > 1 else "slower"
            print(f"  {emoji} {test_name}: {speedup:.2f}x {status}")
        
        avg_speedup = statistics.mean([s for _, s in speedups])
        print(f"\n📊 Average Speedup: {avg_speedup:.2f}x")
        
        if avg_speedup > 1:
            print(f"\n✨ Tachyon is on average {avg_speedup:.2f}x faster than Starlette!")
        else:
            print(f"\n⚠️  Note: Some optimizations are still pending implementation")
    
    print("\n" + "="*80)


def main():
    """Run all benchmarks"""
    print("🚀 TACHYON ENGINE vs STARLETTE - COMPREHENSIVE BENCHMARK")
    print("="*80)
    print(f"Tachyon Available: {'✅ Yes' if TACHYON_AVAILABLE else '❌ No (run: maturin develop)'}")
    print("="*80)
    
    results = BenchmarkResults()
    
    # Run all benchmarks
    test_app_creation(results, iterations=1000)
    test_route_creation(results, iterations=10000)
    test_json_response_creation(results, iterations=10000)
    test_route_addition(results, iterations=1000)
    test_data_structure_operations(results, iterations=50000)
    
    # Display results
    results.print_results()
    print_summary(results)
    
    # Save results
    save_results(results)
    
    print("\n✅ Benchmark complete!")


if __name__ == "__main__":
    main()

