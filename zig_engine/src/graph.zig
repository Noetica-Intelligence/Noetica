const std = @import("std");

pub const EdgeResult = struct {
    weight: f64,
    rel_type: []const u8,
};

pub fn computeEdge(d1_domain: []const u8, d2_domain: []const u8, d1_title: []const u8, d2_title: []const u8) EdgeResult {
    var weight: f64 = 0.0;
    var rel_type: []const u8 = "related_to";
    
    // Heuristic 1: Domain Match
    if (std.mem.eql(u8, d1_domain, d2_domain)) {
        weight += 0.4;
        rel_type = "shares_domain";
    }
    
    // Heuristic 2: Keyword overlap in Title (Mock algorithm)
    if (std.mem.indexOf(u8, d1_title, "Protein") != null and std.mem.indexOf(u8, d2_title, "Protein") != null) {
        weight += 0.8;
        rel_type = "builds_upon";
    }
    
    return EdgeResult{ .weight = weight, .rel_type = rel_type };
}
