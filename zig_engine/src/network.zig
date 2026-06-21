const std = @import("std");

// ─────────────────────────────────────────────────────────────────────────────
// Network Biology Engine — PageRank-Style Centrality & Influence Ranking
//
// After edge computation (graph.zig), this module runs a network analysis
// pass over the full discovery graph to:
//   1. Compute PageRank-style influence score for each node
//   2. Classify nodes as Hub / Bridge / Peripheral / Isolated
//   3. Detect cross-domain bridge nodes (most valuable for cross-disciplinary insights)
//   4. Compute betweenness approximation (how often a node connects clusters)
// ─────────────────────────────────────────────────────────────────────────────

pub const NodeClass = enum {
    Hub,        // High in-degree, high influence — major discovery
    Bridge,     // Connects multiple domains — cross-disciplinary insight
    Peripheral, // Moderate connections — supporting work
    Isolated,   // No meaningful connections — standalone
};

pub const NetworkResult = struct {
    influence_score:   f64,       // PageRank-style score [0, 10]
    centrality_class:  NodeClass, // Hub | Bridge | Peripheral | Isolated
    in_degree:         u32,       // number of edges pointing to this node
    out_degree:        u32,       // number of edges from this node
    domain_bridge:     bool,      // true if connects 2+ distinct domains
    influence_rank:    u32,       // rank among all nodes (1 = most influential)
};

pub const Edge = struct {
    source: usize,  // index into nodes array
    target: usize,
    weight: f64,
};


pub fn computeNetwork(
    allocator: std.mem.Allocator,
    node_count: usize,
    edges: []const Edge,
    domains: []const []const u8,
    initial_scores: []const f64,   // scores from math.zig
) ![]NetworkResult {

    var results = try allocator.alloc(NetworkResult, node_count);
    for (results) |*r| {
        r.* = NetworkResult{
            .influence_score  = 0.0,
            .centrality_class = .Isolated,
            .in_degree        = 0,
            .out_degree       = 0,
            .domain_bridge    = false,
            .influence_rank   = 0,
        };
    }

    // ── Step 1: Count in/out degrees ─────────────────────────────────────────
    for (edges) |e| {
        if (e.source < node_count) results[e.source].out_degree += 1;
        if (e.target < node_count) results[e.target].in_degree  += 1;
    }

    // ── Step 2: PageRank (simplified, 20 iterations) ─────────────────────────
    const damping: f64 = 0.85;
    const base:    f64 = (1.0 - damping) / @as(f64, @floatFromInt(node_count));

    // Seed PageRank from initial_scores (normalized)
    var max_initial: f64 = 1.0;
    for (initial_scores) |s| {
        if (s > max_initial) max_initial = s;
    }

    var pr  = try allocator.alloc(f64, node_count);
    var pr2 = try allocator.alloc(f64, node_count);
    defer allocator.free(pr);
    defer allocator.free(pr2);

    for (0..node_count) |i| {
        pr[i] = if (max_initial > 0) initial_scores[i] / max_initial else 1.0 / @as(f64, @floatFromInt(node_count));
    }

    for (0..20) |_| {
        for (0..node_count) |i| { pr2[i] = base; }

        for (edges) |e| {
            if (e.source >= node_count or e.target >= node_count) continue;
            const out = @as(f64, @floatFromInt(results[e.source].out_degree));
            if (out > 0) {
                pr2[e.target] += damping * pr[e.source] * e.weight / out;
            }
        }

        // Normalize
        var total: f64 = 0.0;
        for (pr2) |v| { total += v; }
        if (total > 0) {
            for (0..node_count) |i| { pr[i] = pr2[i] / total * @as(f64, @floatFromInt(node_count)); }
        } else {
            for (0..node_count) |i| { pr[i] = pr2[i]; }
        }
    }

    // Scale PageRank to [0, 10]
    var max_pr: f64 = 0.001;
    for (pr) |v| { if (v > max_pr) max_pr = v; }
    for (0..node_count) |i| {
        results[i].influence_score = @min(pr[i] / max_pr * 10.0, 10.0);
    }

    // ── Step 3: Domain Bridge Detection ──────────────────────────────────────
    // A node is a bridge if its edges connect to nodes in 2+ different domains
    for (0..node_count) |i| {
        var connected_domains = std.BoundedArray([]const u8, 32){};
        for (edges) |e| {
            if (e.source == i or e.target == i) {
                const other = if (e.source == i) e.target else e.source;
                if (other < domains.len) {
                    const d = domains[other];
                    var already = false;
                    for (connected_domains.slice()) |cd| {
                        if (std.mem.eql(u8, cd, d)) { already = true; break; }
                    }
                    if (!already and connected_domains.len < 32) {
                        connected_domains.append(d) catch {};
                    }
                }
            }
        }
        // Also add own domain
        if (i < domains.len) {
            const own = domains[i];
            var already = false;
            for (connected_domains.slice()) |cd| {
                if (std.mem.eql(u8, cd, own)) { already = true; break; }
            }
            if (!already and connected_domains.len < 32) {
                connected_domains.append(own) catch {};
            }
        }
        results[i].domain_bridge = connected_domains.len >= 3;
    }

    // ── Step 4: Classify nodes ────────────────────────────────────────────────
    // Hub:        influence_score >= 7.0 AND in_degree >= 3
    // Bridge:     domain_bridge == true AND in_degree >= 2
    // Peripheral: in_degree >= 1 OR out_degree >= 1
    // Isolated:   no edges
    for (0..node_count) |i| {
        const in_d  = results[i].in_degree;
        const score = results[i].influence_score;
        results[i].centrality_class =
            if (score >= 7.0 and in_d >= 3)           .Hub
            else if (results[i].domain_bridge and in_d >= 2) .Bridge
            else if (in_d >= 1 or results[i].out_degree >= 1) .Peripheral
            else .Isolated;
    }

    // ── Step 5: Compute influence_rank ────────────────────────────────────────
    // Build sorted index by influence_score descending
    var indices = try allocator.alloc(usize, node_count);
    defer allocator.free(indices);
    for (0..node_count) |i| { indices[i] = i; }

    // Simple insertion sort (N is small — typically < 100 papers per run)
    var idx: usize = 1;
    while (idx < node_count) : (idx += 1) {
        const key = indices[idx];
        var j: isize = @as(isize, @intCast(idx)) - 1;
        while (j >= 0 and results[indices[@intCast(j)]].influence_score < results[key].influence_score) {
            indices[@intCast(j + 1)] = indices[@intCast(j)];
            j -= 1;
        }
        indices[@intCast(j + 1)] = key;
    }

    for (indices, 0..) |node_i, rank| {
        results[node_i].influence_rank = @as(u32, @intCast(rank + 1));
    }

    return results;
}


pub fn nodeClassString(class: NodeClass) []const u8 {
    return switch (class) {
        .Hub        => "Hub",
        .Bridge     => "Bridge",
        .Peripheral => "Peripheral",
        .Isolated   => "Isolated",
    };
}
