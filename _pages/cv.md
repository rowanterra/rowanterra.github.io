---
layout: page
permalink: /cv/
title: cv
nav: true
nav_order: 5
description: Please find my CV below
---

<p><a class="cv-download" href="{{ '/assets/pdf/terra_cv_2026-10-20_web.pdf' | relative_url }}">Download the CV (PDF)</a></p>

<div class="cv-pages">
{% for i in (1..6) %}
  <img src="{{ '/assets/img/cv/terra_cv_2026-10-04_p' | append: i | append: '.png' | relative_url }}" alt="CV page {{ i }} of 6" width="1275" height="1650" loading="lazy">
{% endfor %}
</div>
