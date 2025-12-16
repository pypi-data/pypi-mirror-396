use criterion::{black_box, criterion_group, criterion_main, Criterion};
use tachyon_engine::routing::{PathMatcher, Route};

fn benchmark_path_matching(c: &mut Criterion) {
    let mut matcher = PathMatcher::new();
    
    // Add routes
    matcher.add_route("/", vec!["GET".to_string()]).unwrap();
    matcher.add_route("/users", vec!["GET".to_string()]).unwrap();
    matcher.add_route("/users/{id}", vec!["GET".to_string()]).unwrap();
    matcher.add_route("/users/{id}/posts", vec!["GET".to_string()]).unwrap();
    matcher.add_route("/users/{id}/posts/{post_id}", vec!["GET".to_string()]).unwrap();
    matcher.add_route("/api/v1/resources/{resource_id}", vec!["GET".to_string()]).unwrap();
    
    c.bench_function("match_simple_path", |b| {
        b.iter(|| {
            matcher.match_path(black_box("/users"), black_box("GET"))
        })
    });
    
    c.bench_function("match_single_param", |b| {
        b.iter(|| {
            matcher.match_path(black_box("/users/123"), black_box("GET"))
        })
    });
    
    c.bench_function("match_nested_params", |b| {
        b.iter(|| {
            matcher.match_path(black_box("/users/123/posts/456"), black_box("GET"))
        })
    });
    
    c.bench_function("match_deep_path", |b| {
        b.iter(|| {
            matcher.match_path(black_box("/api/v1/resources/abc-def-123"), black_box("GET"))
        })
    });
}

fn benchmark_route_addition(c: &mut Criterion) {
    c.bench_function("add_route", |b| {
        b.iter(|| {
            let mut matcher = PathMatcher::new();
            matcher.add_route(
                black_box("/users/{id}"),
                vec!["GET".to_string()],
            ).unwrap();
        })
    });
}

criterion_group!(benches, benchmark_path_matching, benchmark_route_addition);
criterion_main!(benches);

