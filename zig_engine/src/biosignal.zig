const std = @import("std");

// ─────────────────────────────────────────────────────────────────────────────
// BioSignal Engine — Domain-Specific Scientific Signal Detector
//
// Scans paper titles and abstracts for high-value scientific signals
// relevant to the Noetica research focus:
//   - FGFR4 / HCC (Hepatocellular Carcinoma) drug discovery
//   - Chronobiology / Circadian pharmacology
//   - Molecular Dynamics simulation
//   - Drug-likeness / ADMET
//   - Graph Neural Networks for biology
//   - AlphaFold / protein structure
//   - CRISPR / gene editing
// ─────────────────────────────────────────────────────────────────────────────

pub const BioSignalResult = struct {
    bonus: f64,           // additive score bonus [0.0, 3.0]
    flags: SignalFlags,   // which specific signals fired
    primary_signal: []const u8, // highest-priority signal name
};

pub const SignalFlags = struct {
    fgfr4_hcc:        bool = false,
    circadian:        bool = false,
    molecular_dynamics: bool = false,
    drug_likeness:    bool = false,
    gnn_biology:      bool = false,
    alphafold_class:  bool = false,
    crispr:           bool = false,
    quantum_bio:      bool = false,
    mrna_therapy:     bool = false,
    llm_science:      bool = false,
};

const FGFR4_KEYWORDS = [_][]const u8{
    "FGFR4", "fgfr4", "fibroblast growth factor receptor 4",
    "hepatocellular carcinoma", "HCC", "sorafenib", "lenvatinib",
    "kinase inhibitor", "selective inhibitor", "liver cancer",
    "FGFR", "FGF19", "tyrosine kinase",
};

const CIRCADIAN_KEYWORDS = [_][]const u8{
    "circadian", "chronotherapy", "CLOCK", "BMAL1", "PER1", "PER2",
    "CRY1", "CRY2", "chronopharmacology", "circadian rhythm",
    "biological clock", "zeitgeber", "melatonin", "chrono-oncology",
    "time-dependent", "diurnal", "ultradian",
};

const MD_KEYWORDS = [_][]const u8{
    "molecular dynamics", "GROMACS", "AMBER", "NAMD", "CHARMM",
    "MM-PBSA", "binding free energy", "100 ns", "100ns", "200ns",
    "force field", "MD simulation", "trajectory analysis",
    "free energy perturbation", "umbrella sampling",
};

const DRUG_KEYWORDS = [_][]const u8{
    "IC50", "Ki", "Kd", "EC50", "bioavailability", "ADMET",
    "Lipinski", "drug-like", "blood-brain barrier", "BBB",
    "pharmacokinetics", "QSAR", "lead compound",
    "docking score", "binding affinity", "pharmacophore",
};

const GNN_BIO_KEYWORDS = [_][]const u8{
    "graph neural", "message passing", "GNN", "graph convolutional",
    "molecular graph", "protein graph", "drug-target interaction",
    "link prediction biology", "knowledge graph biology",
    "attention mechanism protein",
};

const ALPHAFOLD_KEYWORDS = [_][]const u8{
    "AlphaFold", "protein structure prediction", "pLDDT",
    "de novo protein", "protein language model", "ESM",
    "ProGen", "RoseTTAFold", "protein folding",
    "structural biology AI", "contact prediction",
};

const CRISPR_KEYWORDS = [_][]const u8{
    "CRISPR", "Cas9", "Cas12", "Cas13", "base editing",
    "prime editing", "guide RNA", "gene editing",
    "genome editing", "knock-out", "knock-in",
};

const QUANTUM_BIO_KEYWORDS = [_][]const u8{
    "quantum biology", "quantum tunneling enzyme", "photosynthesis quantum",
    "quantum coherence biology", "quantum sensing", "quantum dot biosensor",
};

const MRNA_KEYWORDS = [_][]const u8{
    "mRNA therapy", "mRNA vaccine", "lipid nanoparticle", "LNP",
    "siRNA", "antisense oligonucleotide", "RNA therapeutics",
};

const LLM_SCIENCE_KEYWORDS = [_][]const u8{
    "large language model science", "AI scientist", "GPT chemistry",
    "foundation model biology", "scientific AI", "language model protein",
    "AI hypothesis generation",
};


fn contains_any(text: []const u8, keywords: anytype) bool {
    for (keywords) |kw| {
        if (std.mem.indexOf(u8, text, kw) != null) {
            return true;
        }
    }
    return false;
}


pub fn computeBioSignal(title: []const u8, abstract: []const u8) BioSignalResult {
    // Combine title and abstract for scanning
    // We give title 2x weight by checking it separately
    var bonus: f64 = 0.0;
    var flags = SignalFlags{};
    var primary: []const u8 = "none";
    var best_bonus: f64 = 0.0;

    // ── FGFR4 / HCC (highest priority for this research focus) ───────────────
    if (contains_any(title, FGFR4_KEYWORDS) or contains_any(abstract, FGFR4_KEYWORDS)) {
        flags.fgfr4_hcc = true;
        const b: f64 = if (contains_any(title, FGFR4_KEYWORDS)) 1.5 else 0.9;
        bonus += b;
        if (b > best_bonus) { best_bonus = b; primary = "FGFR4/HCC Research"; }
    }

    // ── Circadian / ChronoBase (core startup focus) ──────────────────────────
    if (contains_any(title, CIRCADIAN_KEYWORDS) or contains_any(abstract, CIRCADIAN_KEYWORDS)) {
        flags.circadian = true;
        const b: f64 = if (contains_any(title, CIRCADIAN_KEYWORDS)) 1.3 else 0.8;
        bonus += b;
        if (b > best_bonus) { best_bonus = b; primary = "Circadian/Chronotherapy"; }
    }

    // ── Molecular Dynamics ────────────────────────────────────────────────────
    if (contains_any(title, MD_KEYWORDS) or contains_any(abstract, MD_KEYWORDS)) {
        flags.molecular_dynamics = true;
        bonus += 0.6;
        if (0.6 > best_bonus) { best_bonus = 0.6; primary = "Molecular Dynamics"; }
    }

    // ── Drug-likeness / ADMET ─────────────────────────────────────────────────
    if (contains_any(title, DRUG_KEYWORDS) or contains_any(abstract, DRUG_KEYWORDS)) {
        flags.drug_likeness = true;
        bonus += 0.5;
        if (0.5 > best_bonus) { best_bonus = 0.5; primary = "Drug Discovery"; }
    }

    // ── GNN for Biology ───────────────────────────────────────────────────────
    if (contains_any(title, GNN_BIO_KEYWORDS) or contains_any(abstract, GNN_BIO_KEYWORDS)) {
        flags.gnn_biology = true;
        const b: f64 = if (contains_any(title, GNN_BIO_KEYWORDS)) 1.0 else 0.6;
        bonus += b;
        if (b > best_bonus) { best_bonus = b; primary = "GNN Biology"; }
    }

    // ── AlphaFold-class ───────────────────────────────────────────────────────
    if (contains_any(title, ALPHAFOLD_KEYWORDS) or contains_any(abstract, ALPHAFOLD_KEYWORDS)) {
        flags.alphafold_class = true;
        bonus += 0.8;
        if (0.8 > best_bonus) { best_bonus = 0.8; primary = "Protein Structure AI"; }
    }

    // ── CRISPR ───────────────────────────────────────────────────────────────
    if (contains_any(title, CRISPR_KEYWORDS) or contains_any(abstract, CRISPR_KEYWORDS)) {
        flags.crispr = true;
        bonus += 0.7;
        if (0.7 > best_bonus) { best_bonus = 0.7; primary = "CRISPR/Gene Editing"; }
    }

    // ── Quantum Biology ──────────────────────────────────────────────────────
    if (contains_any(title, QUANTUM_BIO_KEYWORDS) or contains_any(abstract, QUANTUM_BIO_KEYWORDS)) {
        flags.quantum_bio = true;
        bonus += 0.9;
        if (0.9 > best_bonus) { best_bonus = 0.9; primary = "Quantum Biology"; }
    }

    // ── mRNA Therapeutics ────────────────────────────────────────────────────
    if (contains_any(title, MRNA_KEYWORDS) or contains_any(abstract, MRNA_KEYWORDS)) {
        flags.mrna_therapy = true;
        bonus += 0.6;
        if (0.6 > best_bonus) { best_bonus = 0.6; primary = "mRNA Therapeutics"; }
    }

    // ── LLM for Science ──────────────────────────────────────────────────────
    if (contains_any(title, LLM_SCIENCE_KEYWORDS) or contains_any(abstract, LLM_SCIENCE_KEYWORDS)) {
        flags.llm_science = true;
        bonus += 0.5;
        if (0.5 > best_bonus) { best_bonus = 0.5; primary = "AI for Science"; }
    }

    // Cap bonus at 3.0 to prevent runaway scores
    if (bonus > 3.0) bonus = 3.0;

    return BioSignalResult{
        .bonus          = bonus,
        .flags          = flags,
        .primary_signal = primary,
    };
}
