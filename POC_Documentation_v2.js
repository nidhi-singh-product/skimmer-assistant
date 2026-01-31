const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
        HeadingLevel, AlignmentType, BorderStyle, WidthType, ShadingType,
        PageBreak, Header, Footer, PageNumber, LevelFormat } = require('docx');
const fs = require('fs');

// Skimmer brand colors
const SKIMMER_DARK = "256295";
const NAVY = "160F4E";
const MINT = "AEEBF3";
const LIGHT_GRAY = "F9FAFB";
const MEDIUM_GRAY = "637381";

// Create borders object
const border = { style: BorderStyle.SINGLE, size: 1, color: "D2D4D6" };
const borders = { top: border, bottom: border, left: border, right: border };
const noBorders = { top: { style: BorderStyle.NONE }, bottom: { style: BorderStyle.NONE }, left: { style: BorderStyle.NONE }, right: { style: BorderStyle.NONE } };

// Helper function for header cells
function headerCell(text, width) {
    return new TableCell({
        borders,
        width: { size: width, type: WidthType.DXA },
        shading: { fill: SKIMMER_DARK, type: ShadingType.CLEAR },
        margins: { top: 100, bottom: 100, left: 120, right: 120 },
        children: [new Paragraph({ children: [new TextRun({ text, bold: true, color: "FFFFFF", font: "Arial", size: 22 })] })]
    });
}

// Helper function for regular cells
function cell(text, width) {
    return new TableCell({
        borders,
        width: { size: width, type: WidthType.DXA },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: [new Paragraph({ children: [new TextRun({ text, font: "Arial", size: 22 })] })]
    });
}

const doc = new Document({
    styles: {
        default: { document: { run: { font: "Arial", size: 24 } } },
        paragraphStyles: [
            { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
              run: { size: 36, bold: true, color: NAVY, font: "Arial" },
              paragraph: { spacing: { before: 400, after: 200 }, outlineLevel: 0 } },
            { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
              run: { size: 28, bold: true, color: SKIMMER_DARK, font: "Arial" },
              paragraph: { spacing: { before: 300, after: 150 }, outlineLevel: 1 } },
            { id: "Heading3", name: "Heading 3", basedOn: "Normal", next: "Normal", quickFormat: true,
              run: { size: 24, bold: true, color: NAVY, font: "Arial" },
              paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 2 } },
        ]
    },
    numbering: {
        config: [
            { reference: "bullets", levels: [
                { level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
                  style: { paragraph: { indent: { left: 720, hanging: 360 } } } },
                { level: 1, format: LevelFormat.BULLET, text: "○", alignment: AlignmentType.LEFT,
                  style: { paragraph: { indent: { left: 1440, hanging: 360 } } } }
            ]},
            { reference: "numbers", levels: [
                { level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
                  style: { paragraph: { indent: { left: 720, hanging: 360 } } } }
            ]},
            { reference: "phases", levels: [
                { level: 0, format: LevelFormat.DECIMAL, text: "Phase %1:", alignment: AlignmentType.LEFT,
                  style: { paragraph: { indent: { left: 720, hanging: 720 } } } }
            ]}
        ]
    },
    sections: [{
        properties: {
            page: {
                size: { width: 12240, height: 15840 },
                margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
            }
        },
        headers: {
            default: new Header({
                children: [new Paragraph({
                    alignment: AlignmentType.RIGHT,
                    children: [new TextRun({ text: "Skimmer Pool Care - POC Documentation", color: MEDIUM_GRAY, size: 20 })]
                })]
            })
        },
        footers: {
            default: new Footer({
                children: [new Paragraph({
                    alignment: AlignmentType.CENTER,
                    children: [
                        new TextRun({ text: "Page ", size: 20, color: MEDIUM_GRAY }),
                        new TextRun({ children: [PageNumber.CURRENT], size: 20, color: MEDIUM_GRAY }),
                        new TextRun({ text: " of ", size: 20, color: MEDIUM_GRAY }),
                        new TextRun({ children: [PageNumber.TOTAL_PAGES], size: 20, color: MEDIUM_GRAY })
                    ]
                })]
            })
        },
        children: [
            // TITLE PAGE
            new Paragraph({ spacing: { after: 600 }, children: [] }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { after: 200 },
                children: [new TextRun({ text: "POC Documentation", size: 56, bold: true, color: NAVY, font: "Arial" })]
            }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { after: 600 },
                children: [new TextRun({ text: "Pool Service Technician Knowledge Base", size: 32, color: SKIMMER_DARK, font: "Arial" })]
            }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { after: 100 },
                children: [new TextRun({ text: "Skimmer Pool Care", size: 28, bold: true, color: NAVY })]
            }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                spacing: { after: 100 },
                children: [new TextRun({ text: "Training & Knowledge Tool", size: 24, color: MEDIUM_GRAY })]
            }),
            new Paragraph({ spacing: { after: 600 }, children: [] }),

            // Project info table
            new Table({
                width: { size: 5000, type: WidthType.DXA },
                alignment: AlignmentType.CENTER,
                rows: [
                    new TableRow({ children: [
                        new TableCell({ borders: noBorders, width: { size: 2000, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Date:", bold: true, size: 22 })] })] }),
                        new TableCell({ borders: noBorders, width: { size: 3000, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "January 30, 2026", size: 22 })] })] })
                    ]}),
                    new TableRow({ children: [
                        new TableCell({ borders: noBorders, width: { size: 2000, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Status:", bold: true, size: 22 })] })] }),
                        new TableCell({ borders: noBorders, width: { size: 3000, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "POC Complete - MVP Deployed", size: 22 })] })] })
                    ]}),
                    new TableRow({ children: [
                        new TableCell({ borders: noBorders, width: { size: 2000, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Version:", bold: true, size: 22 })] })] }),
                        new TableCell({ borders: noBorders, width: { size: 3000, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "2.0", size: 22 })] })] })
                    ]}),
                    new TableRow({ children: [
                        new TableCell({ borders: noBorders, width: { size: 2000, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Author:", bold: true, size: 22 })] })] }),
                        new TableCell({ borders: noBorders, width: { size: 3000, type: WidthType.DXA }, children: [new Paragraph({ children: [new TextRun({ text: "Nidhi Singh", size: 22 })] })] })
                    ]})
                ]
            }),

            new Paragraph({ children: [new PageBreak()] }),

            // EXECUTIVE SUMMARY
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Executive Summary")] }),
            new Paragraph({
                spacing: { after: 200 },
                children: [new TextRun({ text: "This document details the complete journey from concept validation to deployed MVP for the Pool Service Technician Knowledge Base. What started as a NotebookLM proof-of-concept has evolved into a fully functional AI assistant deployed on Streamlit Cloud, accessible to the entire team.", size: 24 })]
            }),
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Key Achievements")] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Validated RAG concept with 223 curated sources in NotebookLM (99% accuracy)", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Built custom Streamlit application with ChromaDB vector database", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Created 17 comprehensive topic guides covering pool service knowledge", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Deployed to Streamlit Cloud with team-accessible URL", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Added photo analysis capability using GPT-4o vision", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Implemented Skimmer branding with Perplexity-style UI", size: 24 })] }),

            new Paragraph({ children: [new PageBreak()] }),

            // SECTION: WHY BUILD VS BUY
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("Why Build This vs. Using ChatGPT, Claude, or Perplexity?")] }),
            new Paragraph({
                spacing: { after: 200 },
                children: [new TextRun({ text: "A common question: Why not just tell technicians to use ChatGPT or Perplexity? Here's why a custom knowledge assistant is fundamentally better for our use case:", size: 24 })]
            }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("1. No Hallucinations - Answers Grounded in Verified Sources")] }),
            new Paragraph({
                spacing: { after: 200 },
                children: [new TextRun({ text: "Generic LLMs can confidently provide incorrect information. They might tell a tech to add 2 lbs of chlorine when it should be 0.5 lbs, or suggest a procedure that damages equipment. Our system ", size: 24 }),
                new TextRun({ text: "only answers from curated, verified sources", bold: true, size: 24 }),
                new TextRun({ text: ". If the information isn't in our knowledge base, it says so - it doesn't make things up.", size: 24 })]
            }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("2. Source Citations - Verify Before You Act")] }),
            new Paragraph({
                spacing: { after: 200 },
                children: [new TextRun({ text: "Every answer shows exactly which source documents it came from. A tech can see \"This came from the Pentair pump manual\" or \"This is from CPO certification materials\" and trust it. With ChatGPT, you have no idea where the information originated - it could be from a Reddit comment from 2018.", size: 24 })]
            }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("3. Skimmer Product Knowledge")] }),
            new Paragraph({
                spacing: { after: 200 },
                children: [new TextRun({ text: "ChatGPT doesn't know anything about Skimmer Pro, our mobile app, our web portal, or our specific workflows. We can train this assistant on:", size: 24 })]
            }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Skimmer mobile app features and troubleshooting", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Web portal navigation and best practices", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Our recommended workflows and SOPs", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Integration with customer service history (future)", size: 24 })] }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("4. Consistent, Reliable Answers")] }),
            new Paragraph({
                spacing: { after: 200 },
                children: [new TextRun({ text: "Ask ChatGPT the same question twice and you might get different answers. Our system pulls from the same curated sources every time, ensuring consistency. When a tech asks about chlorine dosing, they get the same verified answer whether it's Monday morning or Friday night.", size: 24 })]
            }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("5. Instantly Updatable")] }),
            new Paragraph({
                spacing: { after: 200 },
                children: [new TextRun({ text: "New product launch? Updated procedure? Regulatory change? We can add new knowledge in minutes. With ChatGPT, you're stuck with whatever was in their training data (often 1-2 years old). Perplexity searches the web but might find outdated forum posts instead of your latest documentation.", size: 24 })]
            }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("6. Photo Analysis + Knowledge = Better Diagnosis")] }),
            new Paragraph({
                spacing: { after: 200 },
                children: [new TextRun({ text: "A tech can upload a photo of green pool water or an equipment error code. Generic AI might identify \"algae\" but won't know your specific treatment protocol. Our system combines GPT-4 vision with our curated knowledge base to provide the exact procedure from our guides.", size: 24 })]
            }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("7. Training Tool for New Technicians")] }),
            new Paragraph({
                spacing: { after: 200 },
                children: [new TextRun({ text: "New hires can learn using the same trusted sources that experienced techs rely on. It's like having a senior tech available 24/7 to answer questions, but with consistent quality and patience.", size: 24 })]
            }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("8. Data Privacy & Control")] }),
            new Paragraph({
                spacing: { after: 200 },
                children: [new TextRun({ text: "When you use ChatGPT, your questions and any customer information mentioned go to OpenAI's servers. With our system, we control the infrastructure, and future versions could run entirely on-premise if needed.", size: 24 })]
            }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("9. Branding & Professionalism")] }),
            new Paragraph({
                spacing: { after: 200 },
                children: [new TextRun({ text: "This is a Skimmer tool, not a generic chatbot. It looks professional, reinforces our brand, and shows customers that Skimmer invests in supporting their technicians.", size: 24 })]
            }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("10. Cost Control")] }),
            new Paragraph({
                spacing: { after: 200 },
                children: [new TextRun({ text: "ChatGPT Plus costs $20/user/month. For a team of 50 technicians, that's $12,000/year - and they still get generic answers. Our system costs pennies per query (OpenAI API usage) and delivers better, more relevant results.", size: 24 })]
            }),

            // Comparison Table
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Quick Comparison")] }),
            new Table({
                width: { size: 100, type: WidthType.PERCENTAGE },
                columnWidths: [3500, 2200, 2200, 1460],
                rows: [
                    new TableRow({ children: [
                        headerCell("Feature", 3500),
                        headerCell("ChatGPT/Claude", 2200),
                        headerCell("Perplexity", 2200),
                        headerCell("Our RAG", 1460)
                    ]}),
                    new TableRow({ children: [
                        cell("Answers from verified sources only", 3500),
                        cell("❌ No", 2200),
                        cell("⚠️ Partial", 2200),
                        cell("✅ Yes", 1460)
                    ]}),
                    new TableRow({ children: [
                        cell("Source citations", 3500),
                        cell("❌ No", 2200),
                        cell("✅ Yes (web)", 2200),
                        cell("✅ Yes", 1460)
                    ]}),
                    new TableRow({ children: [
                        cell("Skimmer product knowledge", 3500),
                        cell("❌ No", 2200),
                        cell("❌ No", 2200),
                        cell("✅ Yes", 1460)
                    ]}),
                    new TableRow({ children: [
                        cell("Consistent answers", 3500),
                        cell("❌ Varies", 2200),
                        cell("❌ Varies", 2200),
                        cell("✅ Yes", 1460)
                    ]}),
                    new TableRow({ children: [
                        cell("Instantly updatable", 3500),
                        cell("❌ No", 2200),
                        cell("⚠️ Web-dependent", 2200),
                        cell("✅ Yes", 1460)
                    ]}),
                    new TableRow({ children: [
                        cell("Photo + knowledge combined", 3500),
                        cell("⚠️ Generic only", 2200),
                        cell("❌ No", 2200),
                        cell("✅ Yes", 1460)
                    ]}),
                    new TableRow({ children: [
                        cell("Branded experience", 3500),
                        cell("❌ No", 2200),
                        cell("❌ No", 2200),
                        cell("✅ Yes", 1460)
                    ]}),
                    new TableRow({ children: [
                        cell("Data control", 3500),
                        cell("❌ Third-party", 2200),
                        cell("❌ Third-party", 2200),
                        cell("✅ Ours", 1460)
                    ]})
                ]
            }),

            new Paragraph({ children: [new PageBreak()] }),

            // SECTION 1: PROBLEM & VISION
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("1. Problem Statement & Vision")] }),
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("The Challenge")] }),
            new Paragraph({
                spacing: { after: 200 },
                children: [new TextRun({ text: "Pool service technicians need quick, reliable access to technical knowledge while in the field. Currently, finding answers requires searching multiple sources (YouTube, forums, manuals) which is time-consuming and often yields inconsistent information.", size: 24 })]
            }),
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("The Vision")] }),
            new Paragraph({
                spacing: { after: 200 },
                children: [new TextRun({ text: "Build an AI-powered knowledge assistant that can answer pool service questions accurately, citing trusted sources, and accessible from a mobile device in the field. The assistant should also be able to analyze photos of equipment and pool issues.", size: 24 })]
            }),

            new Paragraph({ children: [new PageBreak()] }),

            // SECTION 2: TECHNOLOGY
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("2. Technology Overview")] }),
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("What is RAG?")] }),
            new Paragraph({
                spacing: { after: 200 },
                children: [new TextRun({ text: "RAG (Retrieval Augmented Generation) is the technology that powers AI assistants that can answer questions using a specific knowledge base. It works in three steps:", size: 24 })]
            }),
            new Table({
                width: { size: 100, type: WidthType.PERCENTAGE },
                columnWidths: [1500, 3500, 4360],
                rows: [
                    new TableRow({ children: [headerCell("Step", 1500), headerCell("What Happens", 3500), headerCell("Example", 4360)] }),
                    new TableRow({ children: [cell("1. Question", 1500), cell("User asks a question", 3500), cell("\"What causes a pump to lose prime?\"", 4360)] }),
                    new TableRow({ children: [cell("2. Retrieve", 1500), cell("System searches knowledge base", 3500), cell("Finds relevant chunks from topic guides", 4360)] }),
                    new TableRow({ children: [cell("3. Generate", 1500), cell("AI generates answer from context", 3500), cell("Provides answer with source citations", 4360)] })
                ]
            }),
            new Paragraph({ spacing: { after: 200 }, children: [] }),
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Technology Stack")] }),
            new Table({
                width: { size: 100, type: WidthType.PERCENTAGE },
                columnWidths: [3000, 6360],
                rows: [
                    new TableRow({ children: [headerCell("Component", 3000), headerCell("Technology", 6360)] }),
                    new TableRow({ children: [cell("Frontend", 3000), cell("Streamlit (Python web framework)", 6360)] }),
                    new TableRow({ children: [cell("Vector Database", 3000), cell("ChromaDB (in-memory for cloud)", 6360)] }),
                    new TableRow({ children: [cell("Embeddings", 3000), cell("OpenAI text-embedding-3-small", 6360)] }),
                    new TableRow({ children: [cell("Chat Model", 3000), cell("GPT-4o-mini (text), GPT-4o (vision)", 6360)] }),
                    new TableRow({ children: [cell("Hosting", 3000), cell("Streamlit Cloud (free tier)", 6360)] }),
                    new TableRow({ children: [cell("Version Control", 3000), cell("Git + GitHub", 6360)] })
                ]
            }),

            new Paragraph({ children: [new PageBreak()] }),

            // SECTION 3: DEVELOPMENT TIMELINE
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("3. Development Timeline")] }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Phase 1: Knowledge Base Validation (NotebookLM)")] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Created NotebookLM notebook with 223 curated sources", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Ran Q&A testing: 99% accuracy (102/103 questions)", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Validated RAG concept before custom development", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Identified coverage gaps and added authoritative sources", size: 24 })] }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Phase 2: Local RAG Application")] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Built Streamlit app with ChromaDB vector database", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Queried NotebookLM to create 17 topic guides in Markdown", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Implemented chunking strategy (split by ## headers)", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Added photo analysis with GPT-4o vision", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Tested locally with 187 knowledge chunks", size: 24 })] }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Phase 3: Git & GitHub Setup")] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Installed GitHub CLI: brew install gh", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Authenticated with GitHub using device code flow", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Created repository: nidhi-singh-product/skimmer-assistant", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Created .gitignore (excluding API keys, cache, secrets)", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Initial commit and push to GitHub", size: 24 })] }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Phase 4: Streamlit Cloud Deployment")] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Updated app.py for cloud compatibility (in-memory ChromaDB)", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Added secrets management (st.secrets for API key)", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Made repository public for Streamlit Cloud access", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Deployed app with OpenAI API key in secrets", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Successfully deployed and accessible via URL", size: 24 })] }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Phase 5: UI Redesign with Skimmer Branding")] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Reviewed Skimmer Brand Guidelines 2025 (21 pages)", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Applied brand colors: Navy #160F4E, Skimmer Dark #256295, Mint #AEEBF3", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Used brand fonts: Outfit (headers), Roboto (body)", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Implemented Perplexity-style UI with centered hero and quick actions", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Added prominent photo upload in main area", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Created custom SVG logo matching Skimmer symbol", size: 24 })] }),

            new Paragraph({ children: [new PageBreak()] }),

            // SECTION 4: KNOWLEDGE BASE
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("4. Knowledge Base Content")] }),
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("17 Topic Guides Created")] }),
            new Table({
                width: { size: 100, type: WidthType.PERCENTAGE },
                columnWidths: [600, 4000, 4760],
                rows: [
                    new TableRow({ children: [headerCell("#", 600), headerCell("Topic Guide", 4000), headerCell("Key Content", 4760)] }),
                    new TableRow({ children: [cell("1", 600), cell("Water Chemistry Basics", 4000), cell("pH, chlorine, alkalinity, CYA fundamentals", 4760)] }),
                    new TableRow({ children: [cell("2", 600), cell("Advanced Chemistry", 4000), cell("LSI, calcium hardness, metals, stains", 4760)] }),
                    new TableRow({ children: [cell("3", 600), cell("Pool Pumps", 4000), cell("Types, troubleshooting, priming, motor issues", 4760)] }),
                    new TableRow({ children: [cell("4", 600), cell("Pool Filters", 4000), cell("Sand, DE, cartridge, backwashing", 4760)] }),
                    new TableRow({ children: [cell("5", 600), cell("Pool Heaters", 4000), cell("Gas, electric, heat pumps, sizing", 4760)] }),
                    new TableRow({ children: [cell("6", 600), cell("Saltwater Pools", 4000), cell("Salt cells, generators, maintenance", 4760)] }),
                    new TableRow({ children: [cell("7", 600), cell("Algae Treatment", 4000), cell("Green, black, mustard algae, SLAM", 4760)] }),
                    new TableRow({ children: [cell("8", 600), cell("Pool Cleaning", 4000), cell("Vacuuming, brushing, skimming techniques", 4760)] }),
                    new TableRow({ children: [cell("9", 600), cell("Automation Systems", 4000), cell("Controllers, scheduling, smart features", 4760)] }),
                    new TableRow({ children: [cell("10", 600), cell("Safety Compliance", 4000), cell("Chemical handling, OSHA, barriers", 4760)] }),
                    new TableRow({ children: [cell("11", 600), cell("Pool Plumbing", 4000), cell("Pipes, valves, repairs, pressure testing", 4760)] }),
                    new TableRow({ children: [cell("12", 600), cell("Startup & Closing", 4000), cell("Opening procedures, winterization", 4760)] }),
                    new TableRow({ children: [cell("13", 600), cell("Commercial Pools", 4000), cell("Health codes, testing, records", 4760)] }),
                    new TableRow({ children: [cell("14", 600), cell("Customer Communication", 4000), cell("Explaining repairs, handling complaints", 4760)] }),
                    new TableRow({ children: [cell("15", 600), cell("Leak Detection", 4000), cell("Bucket test, dye test, pressure testing", 4760)] }),
                    new TableRow({ children: [cell("16", 600), cell("Seasonal Pool Care", 4000), cell("Spring, summer, fall, winter procedures", 4760)] }),
                    new TableRow({ children: [cell("17", 600), cell("Variable Speed Pumps", 4000), cell("RPM settings, energy savings, installation", 4760)] })
                ]
            }),
            new Paragraph({ spacing: { after: 200 }, children: [] }),
            new Paragraph({
                children: [new TextRun({ text: "Total: 187 knowledge chunks indexed in vector database", bold: true, size: 24 })]
            }),

            new Paragraph({ children: [new PageBreak()] }),

            // SECTION 5: GIT COMMANDS REFERENCE
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("5. Git & GitHub Commands Reference")] }),
            new Paragraph({
                spacing: { after: 200 },
                children: [new TextRun({ text: "For team members new to Git, here are the key commands used in this project:", size: 24 })]
            }),
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Initial Setup")] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "# Install GitHub CLI (Mac)", font: "Courier New", size: 22 })] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "brew install gh", font: "Courier New", size: 22 })] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "", font: "Courier New", size: 22 })] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "# Authenticate with GitHub", font: "Courier New", size: 22 })] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 200 }, children: [new TextRun({ text: "gh auth login", font: "Courier New", size: 22 })] }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Daily Workflow")] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "# Check status of changes", font: "Courier New", size: 22 })] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "git status", font: "Courier New", size: 22 })] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "", font: "Courier New", size: 22 })] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "# Stage changes", font: "Courier New", size: 22 })] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "git add filename.py", font: "Courier New", size: 22 })] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "", font: "Courier New", size: 22 })] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "# Commit with message", font: "Courier New", size: 22 })] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "git commit -m \"Description of changes\"", font: "Courier New", size: 22 })] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "", font: "Courier New", size: 22 })] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "# Push to GitHub (triggers Streamlit redeploy)", font: "Courier New", size: 22 })] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 200 }, children: [new TextRun({ text: "git push origin main", font: "Courier New", size: 22 })] }),

            new Paragraph({ children: [new PageBreak()] }),

            // SECTION 6: APP FEATURES
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("6. Application Features")] }),
            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Core Features")] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Natural language Q&A: Ask questions in plain English", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Source citations: Every answer shows which guides it came from", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Photo analysis: Upload images of equipment or pool issues", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Quick action buttons: Common questions with one click", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Conversation history: Follow-up questions in context", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Mobile-friendly: Works on phones and tablets in the field", size: 24 })] }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Quick Action Buttons")] }),
            new Table({
                width: { size: 100, type: WidthType.PERCENTAGE },
                columnWidths: [3000, 6360],
                rows: [
                    new TableRow({ children: [headerCell("Button", 3000), headerCell("Question Triggered", 6360)] }),
                    new TableRow({ children: [cell("Balance pH levels", 3000), cell("How do I balance pH levels in a pool?", 6360)] }),
                    new TableRow({ children: [cell("Fix pump issues", 3000), cell("How do I troubleshoot a pool pump that won't prime?", 6360)] }),
                    new TableRow({ children: [cell("Green pool fix", 3000), cell("How do I treat a green algae pool?", 6360)] }),
                    new TableRow({ children: [cell("Winter closing", 3000), cell("What are the steps for winterizing a pool?", 6360)] }),
                    new TableRow({ children: [cell("Leak detection", 3000), cell("How do I perform a bucket test for leaks?", 6360)] }),
                    new TableRow({ children: [cell("Variable speed pump", 3000), cell("What RPM settings should I use for a variable speed pump?", 6360)] })
                ]
            }),

            new Paragraph({ children: [new PageBreak()] }),

            // SECTION 7: FILES & STRUCTURE
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("7. Project Files & Structure")] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "KBPooltech/", font: "Courier New", size: 22 })] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "├── skimmer_assistant/", font: "Courier New", size: 22 })] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "│   └── app.py              # Main Streamlit application", font: "Courier New", size: 22 })] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "├── topic_guides/           # 17 markdown knowledge files", font: "Courier New", size: 22 })] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "│   ├── 01_water_chemistry_basics.md", font: "Courier New", size: 22 })] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "│   ├── 02_advanced_water_chemistry.md", font: "Courier New", size: 22 })] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "│   ├── ... (15 more guides)", font: "Courier New", size: 22 })] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "│   └── 17_variable_speed_pumps.md", font: "Courier New", size: 22 })] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "├── requirements.txt        # Python dependencies", font: "Courier New", size: 22 })] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 100 }, children: [new TextRun({ text: "├── .gitignore              # Files to exclude from git", font: "Courier New", size: 22 })] }),
            new Paragraph({ shading: { fill: LIGHT_GRAY, type: ShadingType.CLEAR }, spacing: { after: 200 }, children: [new TextRun({ text: "└── README.md               # Project documentation", font: "Courier New", size: 22 })] }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Key URLs")] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "GitHub Repository: github.com/nidhi-singh-product/skimmer-assistant", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Streamlit App: [Your Streamlit Cloud URL]", size: 24 })] }),

            new Paragraph({ children: [new PageBreak()] }),

            // SECTION 8: ROLLOUT PLAN
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("8. Rollout Plan & Next Steps")] }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Phase 1: Internal Dogfooding (Weeks 1-2)")] }),
            new Paragraph({
                spacing: { after: 100 },
                children: [new TextRun({ text: "Goal: ", bold: true, size: 24 }), new TextRun({ text: "Validate with internal team before broader rollout", size: 24 })]
            }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Share Streamlit URL with Product & Engineering team", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Collect feedback on answer quality, missing topics, UI issues", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Monitor OpenAI API usage and costs", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Create feedback form for structured input", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Fix critical bugs and iterate on UI", size: 24 })] }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Phase 2: Support & Sales Pilot (Weeks 3-4)")] }),
            new Paragraph({
                spacing: { after: 100 },
                children: [new TextRun({ text: "Goal: ", bold: true, size: 24 }), new TextRun({ text: "Test with customer-facing teams", size: 24 })]
            }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Expand to Support team for customer question handling", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Expand to Sales team for demo and prospect questions", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Track most common questions asked", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Identify knowledge gaps from real usage", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Add Skimmer product documentation to knowledge base", size: 24 })] }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Phase 3: Technician Beta (Weeks 5-8)")] }),
            new Paragraph({
                spacing: { after: 100 },
                children: [new TextRun({ text: "Goal: ", bold: true, size: 24 }), new TextRun({ text: "Real-world field testing with actual technicians", size: 24 })]
            }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Select 10-15 beta technicians from partner companies", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Test mobile experience in field conditions", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Test photo analysis with real equipment issues", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Collect feedback on answer accuracy and usefulness", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Refine knowledge base based on real-world gaps", size: 24 })] }),

            new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun("Phase 4: Analytics & Expansion (Weeks 9+)")] }),
            new Paragraph({
                spacing: { after: 100 },
                children: [new TextRun({ text: "Goal: ", bold: true, size: 24 }), new TextRun({ text: "Data-driven improvements and broader rollout", size: 24 })]
            }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Implement usage analytics (most common questions, satisfaction)", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Add more topic guides based on usage patterns", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Consider Skimmer app integration (customer context)", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Evaluate mobile app wrapper for iOS/Android", size: 24 })] }),
            new Paragraph({ numbering: { reference: "bullets", level: 0 }, children: [new TextRun({ text: "Explore voice input for hands-free field use", size: 24 })] }),

            new Paragraph({ children: [new PageBreak()] }),

            // SECTION 9: LESSONS LEARNED
            new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun("9. Lessons Learned")] }),
            new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 150 }, children: [new TextRun({ text: "Validate before building: ", bold: true, size: 24 }), new TextRun({ text: "NotebookLM let us test the concept for free before writing code", size: 24 })] }),
            new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 150 }, children: [new TextRun({ text: "Source quality > quantity: ", bold: true, size: 24 }), new TextRun({ text: "Curated, authoritative sources beat large volumes of mixed quality", size: 24 })] }),
            new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 150 }, children: [new TextRun({ text: "Streamlit Cloud is perfect for POCs: ", bold: true, size: 24 }), new TextRun({ text: "Free, fast deployment, automatic redeployment on git push", size: 24 })] }),
            new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 150 }, children: [new TextRun({ text: "Git is essential: ", bold: true, size: 24 }), new TextRun({ text: "Version control made iteration and deployment seamless", size: 24 })] }),
            new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 150 }, children: [new TextRun({ text: "Vision capabilities add significant value: ", bold: true, size: 24 }), new TextRun({ text: "Photo analysis differentiates from simple chatbots", size: 24 })] }),
            new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 150 }, children: [new TextRun({ text: "Branding matters: ", bold: true, size: 24 }), new TextRun({ text: "Professional appearance increases adoption and trust, even for internal tools", size: 24 })] }),
            new Paragraph({ numbering: { reference: "numbers", level: 0 }, spacing: { after: 150 }, children: [new TextRun({ text: "Custom RAG beats generic LLMs: ", bold: true, size: 24 }), new TextRun({ text: "Grounded answers from verified sources are worth the extra effort", size: 24 })] }),

            new Paragraph({ spacing: { before: 400 }, children: [] }),
            new Paragraph({
                alignment: AlignmentType.CENTER,
                shading: { fill: MINT, type: ShadingType.CLEAR },
                spacing: { before: 200, after: 200 },
                children: [new TextRun({ text: "Document prepared for Skimmer Pool Care Team", size: 24, color: NAVY })]
            }),
        ]
    }]
});

Packer.toBuffer(doc).then(buffer => {
    fs.writeFileSync('/sessions/exciting-beautiful-babbage/mnt/nidhisingh/Desktop/KBPooltech/POC_Documentation_Complete_v2.docx', buffer);
    console.log('Document created successfully!');
});
