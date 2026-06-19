const std = @import("std");

pub const NodeResult = struct {
    score: f64,
    status: []const u8,
    forecast_prob: f64,
};

pub fn computeScore(title: []const u8, abstract: []const u8, source: []const u8) NodeResult {
    var score: f64 = 5.0; 
    if (title.len > 10 and abstract.len > 10) { score += 1.0; }
    
    var multiplier: f64 = 1.0;
    if (std.mem.indexOf(u8, source, "Nature") != null or std.mem.indexOf(u8, source, "Science") != null) {
        multiplier = 1.5;
    }

    score = score * multiplier;
    if (score > 10.0) score = 10.0;

    var status: []const u8 = "Emerging";
    var forecast_prob: f64 = 0.05;
    
    if (score >= 9.0) {
        status = "Breakthrough";
        forecast_prob = 0.85;
    } else if (score >= 7.0) {
        status = "Growing";
        forecast_prob = 0.40;
    }

    // Apply Noetica Civilizational Filters
    if (std.mem.indexOf(u8, title, "Quantum") != null or 
        std.mem.indexOf(u8, title, "CRISPR") != null or 
        std.mem.indexOf(u8, title, "Language Models") != null) 
    {
        forecast_prob += 0.10; 
        if (forecast_prob > 0.99) forecast_prob = 0.99; // Never certainty (Noetica Principle 14)
    }

    return NodeResult{ .score = score, .status = status, .forecast_prob = forecast_prob };
}
