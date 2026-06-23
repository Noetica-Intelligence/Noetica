const std = @import("std");

pub const EdgeResult = struct {
    weight: f64,
    rel_type: []const u8,
};

pub fn computeEdge(d1_domain: []const u8, d2_domain: []const u8, d1_title: []const u8, d2_title: []const u8) EdgeResult {
    var weight: f64 = 0.0;
    var rel_type: []const u8 = "related_to";
    
    // Heuristic 1: Domain Match
    const same_domain = std.mem.eql(u8, d1_domain, d2_domain);
    if (same_domain) {
        weight += 0.3;
        rel_type = "shares_domain";
    }
    
    // Heuristic 2: Substring matches for structural overlap (since allocator isn't available)
    // We check if d1_title and d2_title share high-value conceptual tokens
    const high_value_tokens = [_][]const u8{
        "Network", "Model", "Algorithm", "Graph", "Protein", "Quantum", "Dynamics",
        "Neural", "Structure", "Optimization", "Predict", "Topology", "Function"
    };

    var overlap_count: f64 = 0.0;
    for (high_value_tokens) |token| {
        if (std.mem.indexOf(u8, d1_title, token) != null and std.mem.indexOf(u8, d2_title, token) != null) {
            overlap_count += 1.0;
        }
    }

    if (overlap_count > 0.0) {
        weight += overlap_count * 0.25;
        if (!same_domain and overlap_count >= 2.0) {
            rel_type = "cross_disciplinary_bridge";
            weight += 0.5; // Massive bonus for bridging domains
        } else {
            rel_type = "builds_upon";
        }
    }
    
    if (weight > 1.0) weight = 1.0;

    return EdgeResult{ .weight = weight, .rel_type = rel_type };
}
