const std = @import("std");

pub const NodeResult = struct {
    score: f64,
    status: []const u8,
    forecast_prob: f64,
};

pub fn computeScore(title: []const u8, abstract: []const u8, source: []const u8) NodeResult {
    var base_score: f64 = 0.0;
    
    // 1. Text density & complexity proxy (Novelty / Depth)
    const title_len = @as(f64, @floatFromInt(title.len));
    const abstract_len = @as(f64, @floatFromInt(abstract.len));
    
    if (title_len > 0) {
        base_score += @min(title_len / 50.0, 2.0);
    } else {
        base_score += 0.5;
    }
    
    if (abstract_len > 0) {
        base_score += @min(abstract_len / 300.0, 4.0);
    } else {
        base_score += 1.0;
    }

    // 2. Source Credibility Multiplier
    var multiplier: f64 = 1.0;
    if (std.mem.indexOf(u8, source, "Nature") != null or 
        std.mem.indexOf(u8, source, "Science") != null or 
        std.mem.indexOf(u8, source, "Cell") != null or
        std.mem.indexOf(u8, source, "Lancet") != null) 
    {
        multiplier = 1.8;
    } else if (std.mem.indexOf(u8, source, "arXiv") != null or 
               std.mem.indexOf(u8, source, "bioRxiv") != null or
               std.mem.indexOf(u8, source, "medRxiv") != null) 
    {
        multiplier = 1.2;
    } else if (std.mem.indexOf(u8, source, "Patent") != null or 
               std.mem.indexOf(u8, source, "USPTO") != null) 
    {
        multiplier = 1.5;
    }

    // 3. Composite calculation
    var score = base_score * multiplier;

    // Apply Noetica Civilizational Filters (Biosignals)
    if (std.mem.indexOf(u8, title, "Quantum") != null or 
        std.mem.indexOf(u8, title, "CRISPR") != null or 
        std.mem.indexOf(u8, title, "Language Models") != null or
        std.mem.indexOf(u8, title, "Foundation Model") != null) 
    {
        score += 2.0; 
    }

    if (score > 10.0) score = 10.0;

    var status: []const u8 = "Emerging";
    var forecast_prob: f64 = 0.05 + (score / 20.0);
    
    if (score >= 9.0) {
        status = "Breakthrough";
        forecast_prob += 0.40;
    } else if (score >= 7.0) {
        status = "Growing";
        forecast_prob += 0.20;
    }

    if (forecast_prob > 0.99) forecast_prob = 0.99; // Never certainty (Noetica Principle 14)

    return NodeResult{ .score = score, .status = status, .forecast_prob = forecast_prob };
}
