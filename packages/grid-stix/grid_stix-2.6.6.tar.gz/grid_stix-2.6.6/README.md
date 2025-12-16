# Grid-STIX 2.1 Electrical Grid Cybersecurity Ontology
## The Foundational CITADEL Ontology based on STIX 2.1

Grid-STIX is a comprehensive extension of the STIX (Structured Threat Information Expression) 2.1 ontology specifically designed for electrical grid cybersecurity applications. As the foundational ontology for CITADEL (Critical Infrastructure Trustworthy AI Defense and Evaluation Laboratory), Grid-STIX provides a standardized, machine-readable framework for modeling grid assets, operational technology devices, threats, vulnerabilities, supply chain risks, and security relationships in electrical power systems.

## Key Features

- **Comprehensive Grid Coverage**: Physical assets, OT devices, grid components, sensors, and energy storage systems
- **Zero Trust Architecture**: Policy decision points, enforcement points, trust brokers, and continuous monitoring
- **AMI Infrastructure**: Advanced metering networks, head-end systems, mesh gateways, and MDM systems
- **Advanced Security Modeling**: Attack patterns, vulnerabilities, mitigations, and supply chain risks
- **Critical Grid Relationships**: Power flow, protection, control, and synchronization relationships
- **Supply Chain Security**: Supplier modeling, country of origin tracking, and risk assessment
- **Protocol Support**: DNP3, Modbus, IEC 61850, IEC 60870-5-104, OPC-UA, and IEEE standards
- **Python Code Generation**: Automated STIX-compliant Python class generation from ontologies
- **Interactive Visualization**: Enhanced HTML network graphs with grid-specific categorization
- **STIX 2.1 Compliance**: Full compatibility with STIX threat intelligence ecosystem

## Repository Structure

```
grid-stix/
├── environment.yml                           # Conda/Mamba environment specification
├── Makefile                                  # Build automation and workflows
├── ontology/                                 # OWL ontology files
│   ├── catalog.xml                           # XML catalog for import resolution
│   ├── contexts/                             # Context-specific ontologies
│   │   ├── grid-stix-2.1-cyber-contexts.owl      # Cybersecurity posture and contexts
│   │   ├── grid-stix-2.1-environmental-contexts.owl # Weather, natural disasters
│   │   ├── grid-stix-2.1-operational-contexts.owl   # Grid operating conditions
│   │   └── grid-stix-2.1-physical-contexts.owl      # Physical security contexts
│   ├── core/                                 # Core ontology components
│   │   ├── grid-stix-2.1-assets.owl          # Assets, suppliers, supply chain
│   │   ├── grid-stix-2.1-components.owl      # Grid components, OT devices, sensors
│   │   └── grid-stix-2.1-relationships.owl   # Power flow, protection, control
│   ├── nuclear/                              # Nuclear safeguards and security
│   │   └── grid-stix-2.1-nuclear-safeguards.owl  # Nuclear facility security
│   ├── observables/                          # Observable events and monitoring
│   │   └── grid-stix-2.1-events-observables.owl  # Grid events, alarms, anomalies
│   ├── policy/                               # Security policies and procedures
│   │   └── grid-stix-2.1-policies.owl        # Grid security policies
│   ├── root/                                 # Root ontology integration
│   │   └── grid-stix-2.1-root.owl            # Master ontology file
│   ├── threat/                               # Threat and attack modeling
│   │   └── grid-stix-2.1-attack-patterns.owl # Grid-specific attack patterns
│   └── vocabularies/                         # Controlled vocabularies
│       └── grid-stix-2.1-vocab.owl           # Open vocabularies and protocols
├── python/                                   # Generated Python STIX classes
│   └── grid_stix/                            # Python package structure
├── src/                                      # Source code and tools
│   ├── generator/                            # Python code generation system
│   ├── ontology_checker.py                   # Comprehensive validation script
│   └── owl_to_html.py                        # Enhanced visualization generator
└── tac-ontology/                             # STIX 2.1 base ontologies
```

## Quick Start

### Prerequisites

- **Micromamba** for environment management
- **Java runtime** for Robot (sudo apt install default-jre in Ubuntu)
- **Robot Framework** (OWL toolkit) for ontology operations from https://robot.obolibrary.org/ (and in your PATH)
- **xmllint** for XML validation and formatting

### Environment Setup

Create and activate the development environment:

```bash
make init
```

This creates a `grid-stix` conda environment with all required dependencies including:
- Python 3.12
- RDFLib for ontology processing
- NetworkX & Plotly for visualization
- PyGraphviz for advanced layouts
- Black for code formatting
- Security tools (Bandit)

## 🔧 Development Workflow

### Code Quality & Formatting

Format all Python and OWL files:
```bash
make format
```

Run quality checks without modifications:
```bash
make lint
```

Run comprehensive security analysis:
```bash
make security
```

### Ontology Operations

**Merge all component ontologies:**
```bash
make merge
```
Creates `grid-stix-2.1-full.owl` with all modules integrated.

**Validate ontology consistency:**
```bash
make check
```
Runs comprehensive validation including:
- Class hierarchy connectivity
- Missing domain/range declarations
- Unresolved type references and broken property mappings
- URI naming conventions (kebab-case for classes/properties)
- Label format consistency (snake_case)
- Property declaration validation
- STIX compliance verification
- Supply chain relationship validation

**Generate interactive visualization:**
```bash
make html
```
Creates `grid-stix.html` with enhanced electrical grid visualization.

**Generate Python STIX classes:**
```bash
make generate
```
Creates complete Python package in `python/grid_stix/` with STIX-compliant classes for all ontology entities.

## Visualization

Generate interactive HTML visualizations to explore the ontology:

```bash
make html
```

This creates `grid-stix.html` with enhanced electrical grid visualization featuring:

- **Color-coded categories**: Infrastructure (blue), Security (red), Supply chain (brown)
- **Interactive hover**: Detailed information about each concept  
- **Hierarchical layout**: Clear visualization of STIX inheritance
- **Professional presentation**: Publication-ready titles and legends


## Validation & Quality Assurance

Comprehensive ontology validation to ensure consistency and compliance:

```bash
make check
```

**Validation Categories:**
- **Structural**: Class hierarchy integrity, relationship consistency
- **Semantic**: Domain/range validation, property inheritance, unresolved type references
- **Syntactic**: URI naming conventions (kebab-case), label formatting (snake_case)
- **Grid-specific**: Power system relationship validation
- **STIX compliance**: Proper inheritance from STIX base classes

## Contributing

When contributing to Grid-STIX:

1. **Development Cycle:**
   ```bash
   # Make your changes to appropriate files
   make format        # Format code and OWL files
   make check         # Comprehensive ontology validation
   make generate      # Generate Python classes
   make html          # Generate updated visualization
   ```

2. **Best Practices:**
   - Use kebab-case for class and property URIs (e.g., `der-device`)
   - Use snake_case for rdfs:label values (e.g., `der_device`)
   - Maintain proper STIX inheritance patterns
   - Add comprehensive comments for new concepts
   - Run `make check` to ensure validation passes

3. **File Organization:**
   - Assets & infrastructure → `ontology/core/grid-stix-2.1-assets.owl`
   - Grid equipment → `ontology/core/grid-stix-2.1-components.owl`
   - Relationships → `ontology/core/grid-stix-2.1-relationships.owl`
   - Vocabularies → `ontology/vocabularies/grid-stix-2.1-vocab.owl`

## Current Ontology Status

- **Classes**: 230+ comprehensive classes including grid assets, zero trust components, and AMI infrastructure
- **Relationships**: 40+ critical grid relationships including power flow, protection, and trust verification
- **Protocols**: Complete coverage of major ICS/SCADA protocols (DNP3, Modbus, IEC standards)
- **Zero Trust**: Policy decision points, enforcement points, trust brokers, and continuous monitoring
- **AMI Infrastructure**: Head-end systems, mesh networks, meter data management systems
- **Supply Chain**: Comprehensive supplier risk and verification modeling
- **Python Generation**: Full STIX-compliant Python class generation with all properties
- **Validation**: Clean ontology validation with comprehensive consistency checking

## Documentation & Resources

- **Interactive Visualization**: Run `make html` to explore the complete ontology
- **Validation Reports**: Run `make check` for detailed consistency analysis
- **Grid-STIX Specification**: See inline comments and class definitions
- **STIX 2.1 Reference**: [OASIS STIX 2.1 Specification](https://docs.oasis-open.org/cti/stix/v2.1/)

## About CITADEL

Grid-STIX serves as the foundational ontology for **CITADEL** (Critical Infrastructure Trustworthy AI Defense and Evaluation Laboratory), a comprehensive framework for modeling and analyzing security threats to critical infrastructure. By extending STIX 2.1 with domain-specific concepts for power grid operations, distributed energy resources, and operational technology security, Grid-STIX enables advanced threat intelligence sharing and analysis for critical infrastructure protection.

CITADEL leverages Grid-STIX to provide:
- **Unified threat modeling** across critical infrastructure domains
- **AI-driven defense** capabilities for infrastructure protection
- **Trustworthy evaluation** frameworks for security assessments
- **Standardized data exchange** for threat intelligence sharing

## Acknowledgments

This software was developed under U.S. Department of Energy award DE-CR0000049, issued by the Office of Cybersecurity, Energy Security, and Emergency Response (CESER). The prime contractor on this work was Iowa State University, and the ideas herein are influenced by conversations with them. The submitted manuscript has been created by UChicago Argonne, LLC, operator of Argonne National Laboratory. Argonne, a DOE Office of Science laboratory, is operated under Contract No. DE-AC02-06CH11357. The U.S. Government retains for itself, and others acting on its behalf, a paid-up nonexclusive, irrevocable worldwide license in said article to reproduce, prepare derivative works, distribute copies to the public, and perform publicly and display publicly, by or on behalf of the Government.