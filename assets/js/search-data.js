// get the ninja-keys element
const ninja = document.querySelector('ninja-keys');

// add the home and posts menu items
ninja.data = [{
    id: "nav-about",
    title: "about",
    section: "Navigation",
    handler: () => {
      window.location.href = "/";
    },
  },{id: "nav-publications",
          title: "publications",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/publications/";
          },
        },{id: "nav-tools",
          title: "tools",
          description: "Lab tools and calculators.",
          section: "Navigation",
          handler: () => {
            window.location.href = "/tools/";
          },
        },{id: "nav-cv",
          title: "cv",
          description: "Please find my CV below",
          section: "Navigation",
          handler: () => {
            window.location.href = "/cv/";
          },
        },{id: "nav-people",
          title: "people",
          description: "",
          section: "Navigation",
          handler: () => {
            window.location.href = "/people/";
          },
        },{id: "news-in-this-interview-i-discuss-my-ph-d-projects-and-my-experience-as-an-orise-fellow",
          title: 'In this interview, I discuss my Ph.D. projects and my experience as an...',
          description: "",
          section: "News",},{id: "news-received-the-american-society-of-reclamation-sciences-ph-d-level-memorial-scholarship-award",
          title: 'Received the American Society of Reclamation Sciences Ph.D. Level Memorial Scholarship Award.',
          description: "",
          section: "News",},{id: "news-presenting-computational-approaches-assist-in-critical-mineral-recovery-and-remediation-effort-prioritization-within-mining-affected-systems-at-the-american-society-of-reclamation-sciences-2026-conference-in-laramie-wy",
          title: 'Presenting Computational approaches assist in critical mineral recovery and remediation effort prioritization within...',
          description: "",
          section: "News",},{id: "news-presenting-the-invited-talk-the-mineral-within-the-protein-predicting-structural-and-functional-properties-of-proteins-from-mineralogical-scaffolds-at-gsa-connects-2026-in-denver-co-october-11-14",
          title: 'Presenting the invited talk The Mineral within the Protein: Predicting Structural and Functional...',
          description: "",
          section: "News",},{id: "news-presenting-governed-by-genomes-and-bound-by-eh-ph-guiding-microbial-communities-for-recovery-of-critical-minerals-at-gsa-connects-2026-in-denver-co-october-11-14",
          title: 'Presenting Governed by Genomes and Bound by Eh-pH: Guiding Microbial Communities for Recovery...',
          description: "",
          section: "News",},{id: "news-defending-my-ph-d-dissertation-a-microbiological-basis-for-critical-mineral-and-material-acquisition-from-abandoned-coal-mines-in-pennsylvania-at-duquesne-university",
          title: 'Defending my Ph.D. dissertation, A Microbiological Basis for Critical Mineral and Material Acquisition...',
          description: "",
          section: "News",},{id: "projects-corrplotpy",
          title: 'corrplotpy',
          description: "A Python port of the R package corrplot 0.95, with a style builder that writes the Python or R code for a plot and a side-by-side comparison with R.",
          section: "Projects",handler: () => {
              window.location.href = "/projects/corrplotpy/";
            },},{id: "projects-stock-solutions-calculator",
          title: 'Stock Solutions Calculator',
          description: "Step-by-step solution preparation with automatic mass/volume calculations, bottle labels, and multi-component recipes.",
          section: "Projects",handler: () => {
              window.location.href = "/projects/solutions_calculator/";
            },},{
        id: 'social-email',
        title: 'email',
        section: 'Socials',
        handler: () => {
          window.open("mailto:%72%6F%77%61%6E.%72.%74%65%72%72%61(%61%74)%67%6D%61%69%6C(%64%6F%74)%63%6F%6D", "_blank");
        },
      },{
        id: 'social-github',
        title: 'GitHub',
        section: 'Socials',
        handler: () => {
          window.open("https://github.com/rowanterra", "_blank");
        },
      },{
        id: 'social-linkedin',
        title: 'LinkedIn',
        section: 'Socials',
        handler: () => {
          window.open("https://www.linkedin.com/in/rowan-terra", "_blank");
        },
      },{
        id: 'social-orcid',
        title: 'ORCID',
        section: 'Socials',
        handler: () => {
          window.open("https://orcid.org/0009-0001-3890-705X", "_blank");
        },
      },{
        id: 'social-scholar',
        title: 'Google Scholar',
        section: 'Socials',
        handler: () => {
          window.open("https://scholar.google.com/citations?user=BSpwNNoAAAAJ&hl", "_blank");
        },
      },];
