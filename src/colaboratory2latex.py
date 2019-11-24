#~/usr/bin/env python
# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import base64
import filepath
import textwrap
import time
from tqdm import tqdm
import urllib.parse

class Colaboratory2Latex:

    def __init__(self,url,directory,google_login_id_pw,showMarkdownCell=True,showCodeCell=True,showCodeCellInput=True,showCodeCellOutput=True):
        driver = webdriver.Chrome()
        self.url=urllib.parse.quote(url,safe='')
        login_url="https://accounts.google.com/signin/v2/identifier?hl=ja&passive=true&continue=%s&flowName=GlifWebSignIn&flowEntry=ServiceLogin" % self.url
        driver.get(login_url)
        self.login_google(driver,google_login_id_pw)
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, 'notebook-container')))
        self.title = str(driver.find_element_by_id('doc-name').get_attribute("value"))
        print("open:%s" % self.title)
        ###読み込んでおく
        cells=driver.find_elements_by_class_name("cell")
        print("Collecting Cell Data...")
        pbar=tqdm(total=len(cells))
        for cell in cells:
            actions = ActionChains(driver)
            actions.move_to_element(cell)
            actions.perform()
            pbar.update(1)
        pbar.close()
        ###セルにオプションをせってい
        cell_option={}
        if len(driver.find_elements_by_class_name("sidebar")) and len(driver.find_element_by_class_name("sidebar").find_elements_by_class_name("comment-fragment")):
            option=driver.find_element_by_class_name("sidebar").find_element_by_class_name("comment-fragment").find_element_by_class_name("comment-text").text.split("\n")
            for item in option:
                cell_option_split=item.split(";")
                if cell_option_split[0][0]=="#":
                    cell_option.setdefault(int(cell_option_split[0][1:]),cell_option_split[1])
        ###以下でtexにする
        print("Writing Data...")
        with open(directory,"w") as self.tex:
            self.cell_counter=0
            self.codecell_counter=0
            pbar=tqdm(total=len(cells))
            for cell in cells:
                self.cell_counter+=1
                actions = ActionChains(driver)
                actions.move_to_element(cell)
                actions.perform()
                if self.cell_counter in cell_option.keys():
                    if cell_option[self.cell_counter]=="display:none":
                        #self.codecell_counter+=1
                        pbar.update(1)
                        continue
                if showMarkdownCell and len(cell.find_elements_by_class_name("markdown")):
                    self.getMarkdown(cell)
                if showCodeCell and len(cell.find_elements_by_class_name("codecell-input-output")):
                    self.codecell=cell.find_element_by_class_name("codecell-input-output")
                    self.codecell_counter+=1
                    if showCodeCellInput:
                        self.getCodecellInput(driver)
                    if showCodeCellOutput:
                        self.iframe=self.codecell.find_elements_by_xpath(".//div[@class='outputview']/iframe")
                        if len(self.iframe):
                            self.includegraphics_option="keepaspectratio,width=0.4\hsize"
                            if self.cell_counter in cell_option.keys():
                                if "figureoption:" in cell_option[self.cell_counter]:
                                    self.includegraphics_option=cell_option[self.cell_counter].split(":")[1]
                            driver.switch_to.frame(self.iframe[0])
                            self.getCodecellOutput(driver)
                            driver.switch_to.parent_frame()
                pbar.update(1)
            pbar.close()
        driver.quit()

    def login_google(self,driver,google_login_id_pw):
        login_id,login_pw = google_login_id_pw
        login_id_xpath = '//*[@id="identifierNext"]'
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, login_id_xpath)))
        driver.find_element_by_name("identifier").send_keys(login_id)
        driver.find_element_by_xpath(login_id_xpath).click()
        login_pw_xpath = '//*[@id="passwordNext"]'
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, login_pw_xpath)))
        driver.find_element_by_name("password").send_keys(login_pw)
        time.sleep(1)
        driver.find_element_by_xpath(login_pw_xpath).click()

    def getMarkdown(self,cell):
        markdown=cell.find_element_by_class_name("markdown")
        soup=BeautifulSoup(markdown.get_attribute("innerHTML"),"lxml")
        if len(soup.find_all("svg")):
            soup.find("path").unwrap()
            soup.find("iron-icon").unwrap()
            soup.find("svg").extract()
            soup.find("paper-icon-button").extract()
        for item in soup.find_all("img"):
            item.extract()
        for item in soup.find_all("nobr"):
            item.extract()
        for item in soup.find_all("script"):
            if item["type"]=="math/tex; mode=display":
                item.replace_with("\\[%s\\]" % item.text)
            else:
                item.replace_with("$%s$" % item.text)
        for item in soup.find_all("em"):
            item.replace_with("\\textit{%s}" % item.text)
        for item in soup.find_all("strong"):
            item.replace_with("\\textbf{%s}" % item.text)
        for item in soup.find_all("a"):
            item.replace_with("\\href{%s}{%s}" % (item["href"],item.text))
        for item in soup.find_all("h1"):
            item.replace_with("\\section{%s}" % item.text)
        for item in soup.find_all("h2"):
            item.replace_with("\\subsection{%s}" % item.text)
        for item in soup.find_all("h3"):
            item.replace_with("\\subsubsection{%s}" % item.text)
        for item in soup.find_all("h4"):
            item.replace_with("\\paragraph{%s}" % item.text)
        for item in soup.find_all("h5"):
            item.replace_with("\\subparagraph{%s}" % item.text)
        for item in soup.find_all("li"):
            item.replace_with("\item %s" % item.text)
        for item in soup.find_all("ul"):
            item.replace_with("\\begin{itemize}\n%s\n\\end{itemize}" % item.text)
        for item in soup.find_all("ol"):
            item.replace_with("\\begin{enumerate}\n%s\n\\end{enumerate}" % item.text)
        for item in soup.find_all("blockquote"):
            item.replace_with("\\begin{quote}\n%s\n\\end{quote}" % item.text)
        for item in soup.find_all("hr"):
            item.replace_with("\\hrulefill")
        for item in soup.find_all("p"):
            item=item.replace_with("%s\\\\" % item.text)
        for item in soup.find_all("div"):
            item.unwrap()
        for item in soup.find_all("span"):
            item.unwrap()
        for table in soup.find_all("table"):    
            tabletex="\\begin{table}[H]\n"
            columnlen=0
            for row in table.find_all("tr"):
                columnlen=max(len(row.find_all(["th","td"])),columnlen)
            tabletex+=textwrap.dedent("""
                \\centering\\scriptsize
                \\begin{tabular}{%s}
                \\hline\n""" % ("|l"*columnlen+"|"))
            thead_flag=True
            for row in table.find_all("tr"):
                tr_items=len(row.find_all(["th","td"]))
                item_counter=0
                for item in row.find_all(["th","td"]):
                    txt=""
                    for char in item.text:
                        if char == "\\":
                            txt+="\\\\"
                        elif char in ["{","}","#","$","%","&","_","^"]:
                            txt+="\%s" % char
                        else:
                            txt+=char
                    if item.has_attr("align") and item["align"] in ["left","center","right"]:
                        align=item["align"][0]
                    else:
                        align="l"
                    if item.has_attr("colspan"):
                        colspan=item["colspan"]
                    else:
                        colspan="1"
                    if align=="l" and colspan=="1":
                        tabletex+=txt
                    else:
                        tabletex+="\\multicolumn{%s}{|%s|}{%s}" % (colspan,align,txt)
                    item_counter+=1
                    if item_counter<tr_items:
                        tabletex+=" & "
                    elif thead_flag and len(table.find_all("thead"))>0:
                        tabletex+=" \\\\ \\hline\\hline\n"
                        thead_flag=False
                    else:
                        tabletex+=" \\\\ \\hline\n"
            tabletex+=textwrap.dedent("""\
                \\end{tabular}
                \\end{table}
                """)
            #print(table)
            table.replace_with(tabletex)
        soup.find("html").unwrap()
        soup.find("body").unwrap()
        txt=str(soup)
        txt=txt.replace("&amp;","&")
        txt=txt.replace("_","\_")
        txt=txt.replace("%","\%")
        ###特殊な空白文字を消す
        txt=r"%s" % txt
        txt=txt.encode("utf-8")
        #txt=txt.replace(b"\x09",b"")
        txt=txt.replace(b"\xc2\xa0",b"")
        txt=txt.replace(b"\xe2\x80\x82",b"")
        txt=txt.replace(b"\xe2\x80\x83",b"")
        txt=txt.replace(b"\xe2\x80\x84",b"")
        txt=txt.replace(b"\xe2\x80\x85",b"")
        txt=txt.replace(b"\xe2\x80\x86",b"")
        txt=txt.replace(b"\xe2\x80\x87",b"")
        txt=txt.replace(b"\xe2\x80\x88",b"")
        txt=txt.replace(b"\xe2\x80\x89",b"")
        txt=txt.replace(b"\xe2\x80\x8a",b"")
        txt=txt.replace(b"\xe2\x80\x8b",b"")
        txt=txt.replace(b"\xe3\x80\x80",b"")
        txt=txt.replace(b"\xef\xbb\xbf",b"")
        txt=txt.replace(b"\xe2\x88\xbc",b"$\\succ$")#sampleのためだけに追加
        #U+2588 \xe2\x96\x88 への対応
        txt=txt.decode("utf-8")
        self.tex.write(txt)
    
    def getCodecellInput(self,driver):
        self.tex.write(textwrap.dedent("""
                \\columnratio{0.09}
                \\begin{paracol}{2}
                \\smallskip
                \\begin{cellExecute}[escapechar=~]
                ~\\inputPrompt{%d}~
                \\end{cellExecute}
                \\switchcolumn
                \\begin{codeCell}[escapechar=~]
                """ % self.codecell_counter))
        for item in self.codecell.find_elements_by_class_name("view-line"):
            soup = BeautifulSoup(item.get_attribute("innerHTML"),"lxml")
            soup.find("span").unwrap()
            spans=soup.find_all("span")
            for item in spans:
                if not item.get("class")==None and len(item.get("class")):
                    if item.get("class")[0]=="mtk1":
                        txt=item.text
                        #txt=txt.replace("_","~\_~")
                        txt=txt.replace(u"\xa0", u" ")
                        self.tex.write(txt)
                    else:
                        colorcode=item.get("class")[0]
                        txt="~\\textcolor{%s}{" % colorcode
                        itemtext=item.text.replace(u"\xa0", u" ")
                        itemtext=item.text.replace(u"\xe2\x80\x8b", u"")
                        for char in itemtext:
                            if char == "\\":
                                txt+="}~~\mtkBackslash{%s}~~\\textcolor{%s}{" % (colorcode,colorcode)
                            elif char == "{":
                                txt+="}~~\mtkLeftBrace{%s}~~\\textcolor{%s}{" % (colorcode,colorcode)
                            elif char == "}":
                                txt+="}~~\mtkRightBrace{%s}~~\\textcolor{%s}{" % (colorcode,colorcode)
                            elif char == "#":
                                txt+="}~~\mtkHash{%s}~~\\textcolor{%s}{" % (colorcode,colorcode)
                            elif char == "$":
                                txt+="}~~\mtkDollar{%s}~~\\textcolor{%s}{" % (colorcode,colorcode)
                            elif char == "%":
                                txt+="}~~\mtkPercent{%s}~~\\textcolor{%s}{" % (colorcode,colorcode)
                            elif char == "&":
                                txt+="}~~\mtkAmpersand{%s}~~\\textcolor{%s}{" % (colorcode,colorcode)
                            elif char == "_":
                                txt+="}~~\mtkTilde{%s}~~\\textcolor{%s}{" % (colorcode,colorcode)
                            elif char == "^":
                                txt+="}~~\mtkCaret{%s}~~\\textcolor{%s}{" % (colorcode,colorcode)  
                            else:
                                txt+=char
                        txt+="}~"
                        txt=txt.replace("~\\textcolor{%s}{}~" % colorcode,"")
                        self.tex.write(txt)
            self.tex.write("\n")
        self.tex.write(textwrap.dedent("""\
            \\end{codeCell}
            \\end{paracol}
            """))
        
    def getCodecellOutput(self,driver):
        self.tex.write(textwrap.dedent("""
            \\columnratio{0.09}
            \\begin{paracol}{2}
            \\begin{cellExecute}[escapechar=~]
            ~\\outputPrompt{%d}~
            \\end{cellExecute}
            \\switchcolumn
            \\begin{resultCell}[escapechar=~]
            """ % self.codecell_counter))

        ###stream
        if len(driver.find_elements_by_id("output-body")) and len(driver.find_element_by_id("output-body").find_elements_by_class_name("stream")):
            streams=driver.find_element_by_id("output-body").find_elements_by_class_name("stream")
            for stream in streams:
                self.tex.write(stream.text)
            
        ###pyout
        if len(driver.find_elements_by_class_name("pyout"))>0:
            pyout=driver.find_element_by_class_name("pyout")
            if len(pyout.find_elements_by_class_name("output_text"))>0:
                pyouttext=pyout.find_element_by_class_name("output_text")
                self.tex.write(pyouttext.text)
        self.tex.write(textwrap.dedent("""\
            \\end{resultCell}
            \\end{paracol}
            """))

        ###pyout-table
        if len(driver.find_elements_by_class_name("pyout")):
            pyout=driver.find_element_by_class_name("pyout")
            soup=BeautifulSoup(pyout.get_attribute("innerHTML"),"lxml")
            tables=soup.find_all("table")
            for table in tables:
                self.tex.write("\\begin{table}[H]")
                columnlen=0
                for row in table.find_all("tr"):
                    columnlen=max(len(row.find_all(["th","td"])),columnlen)
                self.tex.write(textwrap.dedent("""
                    \\centering\\scriptsize
                    \\begin{tabular}{%s}
                    \\hline\n""" % ("|l"*columnlen+"|")))
                thead_flag=True
                for row in table.find_all("tr"):
                    tr_items=len(row.find_all(["th","td"]))
                    item_counter=0
                    for item in row.find_all(["th","td"]):
                        txt=""
                        for char in item.text:
                            if char == "\\":
                                txt+="\\\\"
                            elif char in ["{","}","#","$","%","&","_","^"]:
                                txt+="\%s" % char
                            else:
                                txt+=char
                        if item.has_attr("align") and item["align"] in ["left","center","right"]:
                            align=item["align"][0]
                        else:
                            align="l"
                        if item.has_attr("colspan"):
                            colspan=item["colspan"]
                        else:
                            colspan="1"
                        if align=="l" and colspan=="1":
                            self.tex.write(txt)
                        else:
                            self.tex.write("\\multicolumn{%s}{|%s|}{%s}" % (colspan,align,txt))
                        item_counter+=1
                        if item_counter<tr_items:
                            self.tex.write(" & ")
                        elif thead_flag and len(table.find_all("thead"))>0:
                            self.tex.write("\\\\ \\hline \\hline\n")
                            thead_flag=False
                        else:
                            self.tex.write("\\\\ \\hline\n")
                self.tex.write(textwrap.dedent("""\
                    \\end{tabular}
                    \\end{table}
                    """))

        ###get graphs
        if len(driver.find_elements_by_xpath("//img")):
            srclink=driver.find_element_by_xpath("//img").get_attribute("src").split(",")[1]
            img_binary=srclink.replace("%0A","")
            img_decode = base64.b64decode(img_binary)
            filepath.check_figuredirectory()
            with open("%s/fig%s_%d.png" % (filepath.figuredirectory,filepath.dt_now,self.cell_counter),"bw") as f:
                f.write(img_decode)
            self.tex.write(textwrap.dedent("""
                \\begin{figure}[H]
                \\centering
                \\includegraphics[%s]{%s/fig%s_%d.png}
                \\end{figure}
                """ % (self.includegraphics_option,filepath.figuredirectory,filepath.dt_now,self.cell_counter)))