---
layout: archive
title: "Publications and Preprints"
permalink: /publications/
author_profile: true
---

{% if site.author.googlescholar %}
  <div class="wordwrap">You can also find my articles on <a href="{{site.author.googlescholar}}">my Google Scholar profile</a>.</div>
{% endif %}

{% include base_path %}

{% for post in site.publications reversed %}
  {% include archive-single.html %}
{% endfor %}


**Preprints**
1. Online Policy Learning and Inference by Matrix Completion
   With Congyuan Duan, and Dong Xia
1. Computationally efficient and statistically optimal robust low-rank matrix estimation
   With Yinan Shen, Jian-Feng Cai, and Dong Xia

**Publications**
1. Restoration Guarantee of Image Inpainting via Low Rank Patch Matrix Completion
   With Jian-Feng Cai, Jae Kyu Choi, and Guojian Yin 
   *SIAM Journal on Imaging Sciences 17 (3), 1879-1908. [[Journal]](https://epubs.siam.org/doi/abs/10.1137/23M1614456), [[arXiv]](https://arxiv.org/pdf/2309.01328)*







