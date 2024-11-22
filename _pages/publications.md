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
1. On modified Euler schemes for McKean-Valsov stochastic differential equations with super-linear coefficients.  
   With Qingshuo Song, Xiaojie Wang, Zhongqiang Zhang, and Yuying Zhao.  
1. Long-time behaviors of stochastic linear-quadratic optimal control problems.  
   With Sixian Jin, Qingshuo Song and Jiongmin Yong.  

**Publications**
1. Convergence rate of LQG mean field games with common noise.  
   With Qingshuo Song and Jiaxuan Ye.   
   *Mathematical Methods of Operations Research, Vol. 99, 38 pages, 2024. [[Journal]](https://link.springer.com/article/10.1007/s00186-024-00863-2), [[arXiv]](https://arxiv.org/pdf/2307.00695)*
1. The convergence rate of the equilibrium measure for the hybrid LQG mean field game.  
   With Peiyao Lai, Qingshuo Song, and Jiaxuan Ye.  
   *Nonlinear Analysis: Hybrid Systems, Vol. 52, 28 pages, 2024. [[Journal]](https://www.sciencedirect.com/science/article/pii/S1751570X23001255?dgcid=coauthor), [[arXiv]](https://arxiv.org/pdf/2106.04762)*
1. On the graphon mean field game equations: Individual agent affine dynamics and mean field dependent performance functions.  
   With Peter E. Caines, Daniel Ho, Minyi Huang, and Qingshuo Song.  
   *ESAIM: Control, Optimisation and Calculus of Variations, Vol. 28, Article 24, 24 pages, 2022. [[Journal]](https://www.esaim-cocv.org/articles/cocv/abs/2022/01/cocv210017/cocv210017.html), [[arXiv]](https://arxiv.org/pdf/2009.12144)*






