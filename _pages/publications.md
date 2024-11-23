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
1. Federated PCA and Estimation for Spiked Covariance Matrices: Optimal Rates and Efficient Algorithm
   With *T. Tony Cai, Dong Xia, and Anru R. Zhang*
1. Online Policy Learning and Inference by Matrix Completion  [[arXiv]](https://arxiv.org/pdf/2404.17398)  
   With *Congyuan Duan, and Dong Xia*
1. Online tensor learning: Computational and statistical trade-offs, adaptivity and optimal regret  [[arXiv]](https://arxiv.org/pdf/2306.03372)    
   With *Jian-Feng Cai, Yang Chen, and Dong Xia* 
1. Computationally efficient and statistically optimal robust low-rank matrix estimation  
   With *Yinan Shen, Jian-Feng Cai, and Dong Xia*

**Publications**
1. Computationally Efficient and Statistically Optimal Robust High-dimensional Linear Regression  
   With *Yinan Shen, Jian-Feng Cai, and Dong Xia*  
   ***To appear in Annals of Statistics*** [[Journal]](https://www.e-publications.org/ims/submission/AOS/user/submissionFile/60279?confirm=e20d239c)
1. Restoration Guarantee of Image Inpainting via Low Rank Patch Matrix Completion    
   With *Jian-Feng Cai, Jae Kyu Choi, and Guojian Yin*  
   ***SIAM Journal on Imaging Sciences 17 (3), 1879-1908*** [[Journal]](https://epubs.siam.org/doi/abs/10.1137/23M1614456), [[arXiv]](https://arxiv.org/pdf/2309.01328)
1. Generalized low-rank plus sparse tensor estimation by fast Riemannian optimization  
   With *Jian-Feng Cai, and Dong Xia*  
   ***Journal of the American Statistical Association 118 (544), 2588-2604***  [[Journal]](https://www.tandfonline.com/doi/abs/10.1080/01621459.2022.2063131), [[arXiv]](https://arxiv.org/pdf/2103.08895)
1. Provable sample-efficient sparse phase retrieval initialized by truncated power method  
   With *Jian-Feng Cai, Juntao You*  
   ***Inverse Problems 39 (7), 075008***  [[Journal]](https://iopscience.iop.org/article/10.1088/1361-6420/acd8b8/meta), [[arXiv]](https://arxiv.org/pdf/2210.14628)
1. Provable tensor-train format tensor completion by riemannian optimization    
   With *Jian-Feng Cai, and Dong Xia*  
   ***Journal of Machine Learning Research 23 (123), 1-77***  [[Journal]](https://www.jmlr.org/papers/v23/21-1138.html)
1. Image restoration: structured low rank matrix framework for piecewise smooth functions and beyond    
   With *Jian-Feng Cai, Jae Kyu Choi, and Ke Wei*  
   ***Applied and Computational Harmonic Analysis 56, 26-60***  [[Journal]](https://www.sciencedirect.com/science/article/abs/pii/S1063520321000634), [[arXiv]](https://arxiv.org/pdf/2012.06827)









