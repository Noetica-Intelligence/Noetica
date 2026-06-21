const std = @import("std");
const math = @import("math.zig");
const graph = @import("graph.zig");

pub const Discovery = struct {
    id: []const u8,
    title: []const u8,
    abstract: []const u8,
    domain: []const u8,
    source: []const u8,
};

pub fn main() !void {
    const allocator = std.heap.page_allocator;
    
    const input_data = @embedFile("temp_input.json");
    
    
    var parsed = try std.json.parseFromSlice([]Discovery, allocator, input_data, .{
        .ignore_unknown_fields = true,
    });
    defer parsed.deinit();

    const discoveries = parsed.value;
    
    std.debug.print("{{\n", .{});
    std.debug.print("  \"nodes\": [\n", .{});

    // 1. COMPUTE SCORES (NODES)
    for (discoveries, 0..) |d, i| {
        const res = math.computeScore(d.title, d.abstract, d.source);

        std.debug.print(
            \\    {{ "id": "{s}", "title": "{s}", "score": {d:.2}, "status": "{s}", "forecast_probability": {d:.2} }}{s}
        , .{
            d.id, d.title, res.score, res.status, res.forecast_prob,
            if (i == discoveries.len - 1) "\n" else ",\n"
        });
    }
    std.debug.print("  ],\n", .{});
    
    // 2. COMPUTE RELATIONSHIPS (EDGES)
    std.debug.print("  \"edges\": [\n", .{});
    
    var edge_count: usize = 0;
    
    // O(N^2) Knowledge Graph Traversal - Blazing fast in Zig
    for (discoveries, 0..) |d1, i| {
        for (discoveries, 0..) |d2, j| {
            if (i >= j) continue; // Prevent reverse duplicates and self-loops
            
            const edge = graph.computeEdge(d1.domain, d2.domain, d1.title, d2.title);
            
            if (edge.weight > 0.0) {
                if (edge_count > 0) std.debug.print(",\n", .{});
                std.debug.print(
                    \\    {{ "source": "{s}", "target": "{s}", "relationship": "{s}", "weight": {d:.2} }}
                , .{ d1.id, d2.id, edge.rel_type, edge.weight });
                edge_count += 1;
            }
        }
    }
    
    std.debug.print("\n  ]\n", .{});
    std.debug.print("}}\n", .{});
}
