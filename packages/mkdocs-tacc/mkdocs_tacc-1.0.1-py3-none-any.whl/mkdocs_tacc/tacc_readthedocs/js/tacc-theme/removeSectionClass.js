/* To remove "section" class from main content inner wrapper */
/* FAQ: The "section" class conflicts with TACC/Core-Styles o-section pattern */
const sectionDiv = document.querySelector('[role="main"] > div.section');
sectionDiv.classList.remove('section');
sectionDiv.dataset.removedClass = 'section';
