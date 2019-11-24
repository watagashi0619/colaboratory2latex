from colaboratory2latex import Colaboratory2Latex
import yaml
import textwrap
import subprocess
import re
import filepath

superiorpath=filepath.superiorpath
dt_now = filepath.dt_now

with open('%s/settings/settings.yaml' % superiorpath) as yamlfile:
    yml = yaml.load(yamlfile,Loader=yaml.SafeLoader)

if yml["author"] is None:
    author=""
else:
    author=yml["author"]

google_login_id_pw=[yml["google_login"]["id"],yml["google_login"]["password"]]

while True:
    url=input("Please Input Google Colaboratory URL:")
    if url=="" or re.match(r"https://colab\.research\.google\.com/.+",url):
        break
    else:
        print("this is not google colaboratory. Please retry.")

if url=="":
    print("Show sample")
    url="https://colab.research.google.com/notebooks/basic_features_overview.ipynb"

inner_filename_local= "../colaboratory/colaboratory%s" % dt_now
inner_filename="%s/colaboratory/colaboratory%s.tex" % (superiorpath,dt_now)

colaboratory2Latex = Colaboratory2Latex(url,inner_filename,google_login_id_pw)

outer_filename=colaboratory2Latex.title

if yml["title"] is None:
    title=outer_filename.replace("_","\_")
else:
    title=yml["title"]

with open("%s/dist/%s.tex" % (superiorpath,outer_filename),mode="wt") as maintex:
    maintex.write(textwrap.dedent("""
        \\documentclass[10pt,a4paper,dvipdfmx]{jsarticle}
        \\usepackage[dvipdfmx]{graphicx}
        \\input{../settings/settings}
        \\title{%s}
        \\author{%s}
        """ % (title,author)))
    if yml["date"] is None:
        maintex.write("\\date{}")
    elif not yml["date"]=="today": 
        maintex.write("\\date{%s}" % yml["date"])
    maintex.write(textwrap.dedent("""
        \\begin{document}
        \\maketitle

        \\input{%s}

        \\end{document}
        """ % (inner_filename_local)))

cmd=["platex","%s.tex" % outer_filename]
subprocess.run(cmd,cwd=r"%s/dist" % superiorpath)
cmd=["dvipdfmx",outer_filename]
subprocess.run(cmd,cwd=r"%s/dist" % superiorpath)
cmd=["open","%s.pdf" % outer_filename]
subprocess.run(cmd,cwd=r"%s/dist" % superiorpath)
if yml["remove"]["aux"]:
    cmd=["rm","%s.aux" % outer_filename]
    subprocess.run(cmd,cwd=r"%s/dist" % superiorpath)
if yml["remove"]["dvi"]:
    cmd=["rm","%s.dvi" % outer_filename]
    subprocess.run(cmd,cwd=r"%s/dist" % superiorpath)
if yml["remove"]["log"]:
    cmd=["rm","%s.log" % outer_filename]
    subprocess.run(cmd,cwd=r"%s/dist" % superiorpath)
if yml["remove"]["out"]:
    cmd=["rm","%s.out" % outer_filename]
    subprocess.run(cmd,cwd=r"%s/dist" % superiorpath)
if yml["remove"]["tex"]:
    cmd=["rm","%s.tex" % outer_filename]
    subprocess.run(cmd,cwd=r"%s/dist" % superiorpath)