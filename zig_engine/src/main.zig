const std = @import("std");
const math = @import("math.zig");
const graph = @import("graph.zig");
const biosignal = @import("biosignal.zig");
const network = @import("network.zig");

pub const Discovery = struct {
    id: []const u8,
    title: []const u8,
    abstract: []const u8,
    domain: []const u8,
    source: []const u8,
};

pub fn main() !void {
    // 1. Read JSON from STDIN
    var arena = std.heap.ArenaAllocator.init(std.heap.page_allocator);
    defer arena.deinit();
    const allocator = arena.allocator();
    
    const input_data = std.fs.cwd().readFileAlloc(allocator, "input.json", 1024 * 1024 * 100) catch |err| {
        std.debug.print("Failed to read input.json: {}\n", .{err});
        std.debug.print("{{ \"nodes\": [], \"edges\": [] }}\n", .{});
        return;
    };
    
    var parsed = try std.json.parseFromSlice([]Discovery, allocator, input_data, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const discoveries = parsed.value;
    
    // 2. Pre-compute node scores and biosignals
    var initial_scores = try allocator.alloc(f64, discoveries.len);
    var domains = try allocator.alloc([]const u8, discoveries.len);
    
    for (discoveries, 0..) |d, i| {
        const res = math.computeScore(d.title, d.abstract, d.source);
        const bio = biosignal.computeBioSignal(d.title, d.abstract);
        
        var total_score = res.score + bio.bonus;
        if (total_score > 10.0) total_score = 10.0;
        
        initial_scores[i] = total_score;
        domains[i] = d.domain;
    }

    // 3. Generate Edges
    var edges = std.ArrayList(network.Edge).init(allocator);
    var edge_outputs = std.ArrayList(graph.EdgeResult).init(allocator);
    
    for (discoveries, 0..) |d1, i| {
        for (discoveries, 0..) |d2, j| {
            if (i >= j) continue;
            
            const edge = graph.computeEdge(d1.domain, d2.domain, d1.title, d2.title);
            if (edge.weight > 0.0) {
                try edges.append(.{ .source = i, .target = j, .weight = edge.weight });
                try edge_outputs.append(edge);
            }
        }
    }
    
    // 4. Compute Network Graph PageRank
    const net_results = try network.computeNetwork(allocator, discoveries.len, edges.items, domains, initial_scores);
    
    // 5. Write Output
    std.debug.print("{{\n", .{});
    std.debug.print("  \"nodes\": [\n", .{});

    for (discoveries, 0..) |d, i| {
        const bio = biosignal.computeBioSignal(d.title, d.abstract);
        const net = net_results[i];
        
        std.debug.print(
            \\    {{ "id": "{s}", "title": "{s}", "score": {d:.2}, "primary_signal": "{s}", "network_rank": {d}, "influence": {d:.2}, "centrality": "{s}" }}{s}
        , .{
            d.id, d.title, initial_scores[i], bio.primary_signal, net.influence_rank, net.influence_score, network.nodeClassString(net.centrality_class),
            if (i == discoveries.len - 1) "\n" else ",\n"
        });
    }
    std.debug.print("  ],\n", .{});
    
    std.debug.print("  \"edges\": [\n", .{});
    for (edges.items, 0..) |e, idx| {
        const d1 = discoveries[e.source];
        const d2 = discoveries[e.target];
        const out = edge_outputs.items[idx];
        
        std.debug.print(
            \\    {{ "source": "{s}", "target": "{s}", "relationship": "{s}", "weight": {d:.2} }}{s}
        , .{ d1.id, d2.id, out.rel_type, out.weight,
             if (idx == edges.items.len - 1) "\n" else ",\n"
        });
    }
    std.debug.print("\n  ]\n", .{});
    std.debug.print("}}\n", .{});
}
