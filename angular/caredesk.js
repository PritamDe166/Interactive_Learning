/* =========================================================================
   caredesk.js: the running example shared by every Angular page.
   Each page builds one more piece of "CareDesk", a small clinic portal.

   On a page:  <div class="cd-trail" data-stage="5"></div>
               <script src="caredesk.js"></script>   (after explainer-kit.js)
   The strip shows which step of the app this page is, what it adds,
   and links to the previous and next steps.
   The roadmap (index.html) reads CareDesk.STAGES for its "adds" lines.
   ========================================================================= */
(function () {
  const STAGES = [
    { file: 'app-boot.html', t: 'How an Angular app boots', adds: 'Create the CareDesk shell with ng new and get a title on screen' },
    { file: 'typescript.html', t: 'TypeScript for Angular', adds: 'Describe the data: Patient and Triage types' },
    { file: 'components.html', t: 'Components & templates', adds: 'Split the page into Header, PatientList and PatientCard components' },
    { file: 'data-binding.html', t: 'Data binding', adds: 'Show patient details, highlight urgent cases, select a card, search box' },
    { file: 'parent-child.html', t: 'Parent ↔ child data flow', adds: 'PatientList hands a patient down to PatientCard; the card reports back up' },
    { file: 'lifecycle.html', t: 'Lifecycle hooks', adds: 'Start a waiting-time clock when a card appears, stop it when it goes' },
    { file: 'change-detection.html', t: 'Change detection', adds: 'A live clock in the header, and which components refresh when' },
    { file: 'signals.html', t: 'Signals', adds: 'Search, filtered list and counts as computed signals' },
    { file: 'control-flow.html', t: 'Template control flow', adds: 'A card per patient with @for, an empty state, triage badges' },
    { file: 'services-di.html', t: 'Services & dependency injection', adds: 'Move patients into a PatientStore service shared by list and header' },
    { file: 'routing.html', t: 'Routing', adds: 'Pages: patient list, patient details, not found' },
    { file: 'guards-login.html', t: 'Route guards & login flow', adds: 'A login page, a guard on patient pages, a token on API calls' },
    { file: 'template-forms.html', t: 'Template-driven forms', adds: 'Book an appointment with an ngModel form' },
    { file: 'reactive-forms.html', t: 'Reactive forms & Signal Forms', adds: 'Register a new patient with a typed form model' },
    { file: 'http.html', t: 'HTTP, resource & RxJS basics', adds: 'Load patients from an API and save appointments' }
  ];
  function trail(el) {
    const n = +el.dataset.stage, s = STAGES[n - 1], prev = STAGES[n - 2], next = STAGES[n];
    const dots = STAGES.map((x, i) => `<a href="${x.file}" class="${i + 1 < n ? 'done' : i + 1 === n ? 'now' : ''}" title="Step ${i + 1}: ${x.t}" aria-label="Step ${i + 1}: ${x.t}"></a>`).join('');
    el.innerHTML = `<div class="cd-top"><span class="cd-brand">Building CareDesk</span><span class="cd-step">step ${n} of ${STAGES.length}</span></div>
      <div class="cd-dots">${dots}</div>
      <p class="cd-adds"><b>This page adds:</b> ${s.adds}.</p>
      <div class="cd-nav">${prev ? `<a href="${prev.file}">← ${n - 1}. ${prev.t}</a>` : '<span></span>'}${next ? `<a href="${next.file}">${n + 1}. ${next.t} →</a>` : ''}</div>`;
  }
  window.CareDesk = { STAGES, trail };
  document.querySelectorAll('.cd-trail').forEach(trail);
})();
