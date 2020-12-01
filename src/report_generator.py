import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
import matplotlib.pyplot as plt
import dataframe_image as dfi
import fpdf as pdf
import plotly
import plotly.graph_objects as go
from matplotlib import cm
import dataframe_image as dfi
from fpdf import FPDF
import PIL.Image as Image
import os
import time
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import io
from PyPDF2 import PdfFileReader, PdfFileWriter

#fallidos.set_index(['PO','fecha'], inplace=True)
def hover(hover_color="#ffff99"):
    return dict(selector="tr:hover",
                props=[("background-color", "%s" % hover_color)])

styles = [
    hover(),
    dict(selector="th", props=[("font-size", "210%"),('background-color', 'white'),('border-color','white'),##AB85FF
                               ("text-align", "center"),('border-style','solid'),('border-width','0px'), ('width', '200px')]),
    dict(selector="caption", props=[("caption-side", "top"),("font-size", "300%")]),    
  dict(selector = "th:first-child", props = [('display', 'none')])
]

def pie_function(x,y,title,title_color,save,color):
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(aspect="equal"))
    def func(pct, allvals):
        absolute = int(pct/100.*np.sum(allvals))
        return "{:.1f}%\n({:d})".format(pct, absolute)

    def make_autopct(values):
        def my_autopct(pct):
            total = sum(values)
            val = int(round(pct*total/100.0))
            return '{p:.0f}%'.format(p=pct,v=val)
        return my_autopct

    wedges, texts, autotexts = ax.pie(y, autopct=make_autopct(y),colors=color,
                                      textprops=dict(color="w"))

    ax.legend(wedges, x, prop={'size': 25},
              loc="center left",
              bbox_to_anchor=(1, 0, 0.5, 1))

    for w in wedges:
        w.set_linewidth(2)
        w.set_edgecolor('white')


    plt.setp(autotexts, size=20, weight="bold")
    ax.set_title(title, color=title_color,weight='bold', size=20)
    plt.savefig(save,bbox_inches='tight',transparent=True)
    #plt.show()

###
def bar_function(df,color,save, title, title_color):#,title,title_color,save,color):
    ax=df.plot(kind='bar',cmap=color, edgecolor='black',alpha=.9,linewidth=3,width=1/3,fontsize=20, position=0.5,figsize=(10,5))
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    if (len(df)>4) | (len('-'.join('-'.join(df.index)))>40):
        rot=45
    else:
        rot=0
    ax.spines['left'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    #ax.spines['bottom'].set_visible(False)
    ax.patch.set_alpha(0.01)
    ax.get_legend().remove()
    plt.setp(ax.get_xticklabels(), rotation=rot, ha="center")
    ax.set_xlabel('')
    ax.set_ylabel('')
    ax.set_title(title, color=title_color,weight='bold', size=20)
    plt.savefig(save, facecolor=ax.get_facecolor(), edgecolor='none',bbox_inches='tight')

def title_function(title,size,color,save):
    fig = go.Figure()
    fig.add_trace(go.Indicator(
                    domain = {'x': [0,1], 'y': [0,1]},
                title = {
                    "font": {
            "size": size,
            "color": color,
            "family": "serif"
          }, 
       'text': title}))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        autosize=True,
        margin=dict(
            l=200,
            r=200,
            b=100,
            t=100,
            pad=0
        ))
    fig.write_image(save)
    #fig.show() 

def report_generation(input_data):
    col_maps=[cm.Purples_r ,  cm.Blues_r , cm.Greens_r , cm.YlGnBu_r ,  cm.Oranges_r ,  cm.rainbow , cm.YlGn_r ,  cm.ocean , 
           cm.gnuplot , cm.gnuplot2 , cm.CMRmap , cm.cubehelix , cm.brg ,  cm.gist_rainbow,
          cm.jet , cm.nipy_spectral ,  cm.gist_ncar,cm.gist_earth , cm.terrain , cm.gist_stern,cm.BuPu_r ]
    
    board_user_info = input_data['data']['users_info']
    test_data =input_data['data']['work_info']

    j=0
    k=0
    ## Front Image ###
    #page0 = Image.open('Img/1.png', 'r')
    page = Image.open('Img/2.png', 'r')
    text_img = Image.new('RGBA', (1728,2304), (0, 0, 0, 0))
    text_img.paste(page, (0,0))

    ### Image to PDF ####
    doc_w = 1728
    doc_h = 2304
    pdf = FPDF(unit='pt',format=(doc_w,doc_h))
    pdf.set_margins(0,0,0)
    pdf.add_page()
    pdf.image('Img/1.png', type='PNG', link='')


    for workspace in test_data:
        workspace_title=workspace['workspace']
        title_function(workspace_title,80,"#52B62B",'Img/title'+str(j)+'.png')
        for workspace_user in board_user_info:
            workspace_user_title=workspace_user['workspace']
            if workspace_user_title==workspace_title:
                for board in workspace['workspace_data']:
                    columns_len = len(board['columns'])
                    board_name = board['board']
                    if columns_len < 1:
                        pass
                    else:
                        for board_user in workspace_user['workspace_data']:
                            board_user_name = board_user['board_name']
                            if board_user_name==board_name:
                                ### Generates the Title ###
                                #title_function(board_name,80,"#52B62B",'title'+str(j)+'.png')
                                #print(f'board_name: {board_name}')
                                for i in range(len(board['columns'])):
                                    ##### Data General ######
                                    col=board['columns'][i]['col_name']
                                    #print(f'columns:{col}')
                                    x=board['columns'][i]['x']
                                    y=board['columns'][i]['y']
                                    d={col: x, 'Frequency': y}
                                    #### Generates the data frame and sends it to image
                                    df = pd.DataFrame(data=d)
                                    #df=df.T.reset_index().T     #Add headers as rows
                                    #print(df)#df
                                    with pd.option_context('display.precision', 1):
                                        html = df.style.set_properties(**{'text-align': 'center', 'background-color':'white', 'border-color': 'white'}).set_table_styles(styles).set_properties(**{'text-align': 'center',"font-size": "200%",'border-style':'solid','border-width':'0px','border-color': 'white'})
                                    html
                                    dfi.export(html,'Img/Table'+str(j)+'.png')
                                    ### Generates Pie Chart
                                    color_title=col_maps[j](np.arange(len(x)+2)/(len(x)+2))
                                    pie_function(x,y,board_name+' by '+col,col_maps[j](1) ,'Img/pie'+str(j)+'.png',color_title)   

                                    ####Put all images together in a page of png
                                    if k>2:
                                        ### Saves merged image
                                        text_img.save("Img/final_image"+str(j)+".png", format="png")
                                        page = Image.open('Img/2.png', 'r')
                                        text_img = Image.new('RGBA', (1728,2304), (0, 0, 0, 0))
                                        text_img.paste(page, (0,0))
                                        ### Merged Image to pdf
                                        image_path = "Img/final_image"+str(j)+".png"
                                        #print("\nAdding Image...")
                                        pdf.image(image_path, type='PNG', link='') 
                                        k=0
                                    #Paste Title
                                    try:
                                        title = Image.open('Img/title'+str(j)+'.png', 'r')
                                        text_img.paste(title, (600,690*k), mask=title)
                                    except:
                                        title=0
                                    #Paste Table
                                    table= Image.open('Img/table'+str(j)+'.png', 'r')
                                    text_img.paste(table, (160,350+(690*k)), mask=table)

                                    #Paste Pie Chart
                                    pie = Image.open('Img/pie'+str(j)+'.png','r')
                                    text_img.paste(pie, (680,200+(690*k)))
                                    #print(k)
                                    k=k+1
                                    j=j+1
                                    color_num=j
                                #### Data User ######
                                x2=[ele['user_name'] for ele in board_user['users_workload']]
                                y2=[ele['user_count'] for ele in board_user['users_workload']]
                                d2={col: x2, 'Frequency': y2}
                                #### Generates the data frame and sends it to image
                                df2 = pd.DataFrame(data=d2)
                                #df=df.T.reset_index().T     #Add headers as rows
                                #print(df2)#df
                                with pd.option_context('display.precision', 1):
                                    html = df2.style.set_properties(**{'text-align': 'center', 'background-color':'white', 'border-color': 'white'}).set_table_styles(styles).set_properties(**{'text-align': 'center',"font-size": "200%",'border-style':'solid','border-width':'0px','border-color': 'white'})
                                html
                                dfi.export(html,'Img/Table2'+str(j)+'.png')
                                ### Users Bar Chart
                                df2=df2.set_index(df2.columns[0])
                                bar_function(df2,col_maps[i],save='Img/bar'+str(j)+'.png', title=board_name+' by User', title_color=col_maps[color_num](1))
                                ####Put all images together in a page of png
                                if k>2:
                                    ### Saves merged image
                                    text_img.save("Img/final_image"+str(j)+".png", format="png")
                                    page = Image.open('Img/2.png', 'r')
                                    text_img = Image.new('RGBA', (1728,2304), (0, 0, 0, 0))
                                    text_img.paste(page, (0,0))
                                    ### Merged Image to pdf
                                    image_path = "Img/final_image"+str(j)+".png"
                                    #print("\nAdding Image...")
                                    pdf.image(image_path, type='PNG', link='') 
                                    k=0         
                                tab2 = Image.open('Img/Table2'+str(j)+'.png', 'r')
                                text_img.paste(tab2, (160,300+(690*k)), mask=tab2)
                                bar = Image.open('Img/bar'+str(j)+'.png','r')
                                text_img.paste(bar, (900,200+(690*k)), mask=bar)
                                k=k+1
                                j=j+1 

    ### Final Image ###
    text_img.save("Img/final_image"+str(j)+".png", format="png")
    ### Final PDF ####
    image_path = "Img/final_image"+str(j)+".png"
    #print("\nAdding Image...")
    pdf.image(image_path, type='PNG', link='') 
    output_name = 'Img/test_background.pdf'
    #print('\nProcessing output pdf...')#
    pdf.output(output_name, 'F')
    #print("\nPDF exported successfully!")
    readfile= 'Img/test_background.pdf'
    outfile= 'Final_Report.pdf'
    pdfReader = PdfFileReader(open(readfile, 'rb'))
    pdfFileWriter = PdfFileWriter()
    numPages = pdfReader.getNumPages()
    pagelist = [0]
    for index in range(0, numPages):
        if index not in pagelist:
            pageObj = pdfReader.getPage(index)
            pdfFileWriter.addPage(pageObj)
    pdfFileWriter.write(open(outfile, 'wb'))