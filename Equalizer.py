import streamlit as st
import streamlit_vertical_slider  as svs
import streamlit.components.v1 as components
import scipy.fft as fourier
import numpy as np
import librosa 
import math
import matplotlib.pyplot as plt 
import soundfile
import pygame
import pandas as pd
import time
import altair as alt
import mpld3


st.set_page_config(page_title="Equalizer", page_icon=":headphones:",layout="wide")

if 'uploadedFile' not in st.session_state:
    st.session_state['uploadedFile']=None
    st.session_state['modified_wav_file']=None  
    st.session_state['radio_check']=0 
    st.session_state['modified_data']=None 
    st.session_state['fourierValues']=[]   
    st.session_state['size']=0 
    st.session_state['paused']=False 
    st.session_state['play_original']=False 
    st.session_state['change_sound_mode_bool']=False
    

    

          
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

button_style = """
        <style>
        .stButton > button {
            width: 90px;
            height: 35px;
        }
        </style>
        """
st.markdown(button_style, unsafe_allow_html=True)

def plot_animation(df):
    lines = alt.Chart(df).mark_trail().encode(
            x=alt.X("x_axis", axis=alt.Axis(title='Time'),scale=alt.Scale(domain=(0,st.session_state['time'][-1]))),
            y=alt.Y('y_axis', axis=alt.Axis(title='Magnitude')),
        ).properties(
            width=1020,
            height=150
        )
    return lines


def static(file):
   df =file.iloc[0:st.session_state['size']]
   lines = plot_animation(df)
   st.altair_chart(lines) 

def realtime(file):
    df =file
    lines = plot_animation(df)
    line_plot = st.altair_chart(lines)
    N = df.shape[0]
    if not st.session_state['paused']:      
        st.session_state['size'] = 0    
    for i in range(0, N):

        step_df = df.iloc[0:st.session_state['size']]
        lines = plot_animation(step_df)
        line_plot = line_plot.altair_chart(lines)
        if st.session_state['size'] < N-1:
            st.session_state['size'] =st.session_state['size'] + 1
        else:
            if pygame.mixer.get_init() is not None:
                pygame.mixer.quit() 
            st.session_state['paused']=False    
        time.sleep(.001)
    st.experimental_rerun()   

def fourier_transform(x,sampleRate):
    fourierValue=fourier.rfft(x)
    frequency=fourier.rfftfreq(len(x),1/(sampleRate))
    return frequency,fourierValue

def add_new_uploaded_file ():
    if st.session_state['uploadedFileCheck'] is not None:
        st.session_state['uploadedFile']=st.session_state['uploadedFileCheck']
        file=st.session_state['uploadedFile']
        if file.type=='audio/wav':
            st.session_state["dataArray"],sampleRate= librosa.load(st.session_state['uploadedFileCheck'],sr=44100,duration=10) #reading the sampling number of file
            st.session_state['FileLength']=len(st.session_state["dataArray"])
            st.session_state['time']=np.arange(0,st.session_state['FileLength'])/sampleRate
        else :
            file=pd.read_csv(file)
            time =file.iloc[:,0]
            st.session_state['dataArray']=file.iloc[:,1].to_numpy()
            st.session_state['time']=time
            st.session_state['FileLength']=len(st.session_state["dataArray"])
            sampleRate=1/(time[1]-time[0])
        
        st.session_state['modified_data']=st.session_state.dataArray.copy()
        frequency,fourierValues=fourier_transform(st.session_state["dataArray"],sampleRate)
        st.session_state['mainFourierValues']=fourierValues.copy()
        st.session_state['fourierValues']=fourierValues.copy()
        st.session_state['frequency']=frequency
        st.session_state['maxFrequency']=int (sampleRate/2)
        st.session_state['sampleRate']=sampleRate
        st.session_state['modified_wav_file']=None
        st.session_state['paused']=False 
        st.session_state['size'] = 0
        if pygame.mixer.get_init() is not None:
            pygame.mixer.quit() 

def change_frequency(sliderKey,sliderValue):
    maxFrequency=st.session_state['maxFrequency'] 
    max=new_dict['max']
    maxFrequencyRange=max[sliderKey-1]
    min=new_dict['min']
    minFrequencyRange=min[sliderKey-1]            
    pointsPerFrequency=int (len(st.session_state['frequency'])/maxFrequency)
    frequencyRange=[minFrequencyRange*pointsPerFrequency,maxFrequencyRange*pointsPerFrequency]
    dataCopy=st.session_state['mainFourierValues'][frequencyRange[0]:frequencyRange[1]].copy()
    st.session_state.fourierValues[frequencyRange[0]:frequencyRange[1]]= dataCopy*(sliderValue)  

def control_music(control):
       if st.session_state['uploadedFile'] is not None:
        if (not st.session_state['play_original']) and (st.session_state['modified_wav_file'] is not None):
            wav_file=st.session_state['modified_wav_file']
            data=pd.DataFrame({'y_axis':st.session_state['modified_data'][::1800],'x_axis':st.session_state['time'][::1800]})
        else:
            wav_file=file
            data=pd.DataFrame({'y_axis':st.session_state["dataArray"][::1800],'x_axis':st.session_state['time'][::1800]})

        if control== "play":
            if pygame.mixer.get_init() is not None:
              pygame.mixer.music.unpause() 
            else:   
                pygame.mixer.init()
                pygame.mixer.music.load(wav_file)
                pygame.mixer.music.play()
            realtime(data)  


        elif control== "Stop":
                if pygame.mixer.get_init() is not None:
                    pygame.mixer.music.pause()
                static(data)


def maleFemaleChange():
    sampleRate =st.session_state.sampleRate
    shiftBy=st.slider('change Voice',min_value=-50,max_value=50,value=0)
    st.session_state.modified_data=librosa.effects.pitch_shift(st.session_state.dataArray ,sampleRate,n_steps=shiftBy)

def make_sliders():
    if radio_check=="Male Female":
        maleFemaleChange()
    else:
        groups = [  ('slider1',0),
                ('slider2',0),
                ('slider3',0),
                ('slider4',0),
                ('slider5',0),
                ('slider6',0),
                ('slider7',0),
                ('slider8',0),
                ('slider9',0),
                ('slider10',0),]
        
        sliders = {}
        sliders_number=new_dict['number_of_sliders']
        columns = st.columns(sliders_number,gap='small')

        for idx in range(sliders_number):
            min_value = 0
            max_value = 2
            key = idx+1
            with columns[idx]:
                
                sliders[key] = svs.vertical_slider(key=key, default_value=1,
                    step=0.1, min_value=min_value, max_value=max_value)
                if sliders[key] == None:
                    sliders[key]  = 0
                else:
                    change_frequency(key,sliders[key])
                st.caption(new_dict['names_of_sliders'][key-1])

def play_buttons():
        global Apply
        col1,col2=st.sidebar.columns([1,1])
        if col1.button("Play"):
            control_music("play")  
        else: 
            control_music("Stop")

        if col1.button("Stop"):
            st.session_state['paused']=True    
        
        st.session_state['play_original']=col1.checkbox("Play Original",value=False)
        Apply =col2.button("Apply")

def apply_action():
        if radio_check !='Male-Female':
            st.session_state['modified_data']=fourier.irfft(st.session_state['fourierValues'],n=st.session_state['FileLength'])
        if pygame.mixer.get_init() is not None:
            pygame.mixer.quit()
        st.session_state['paused']=False  
        soundfile.write('tem1.wav', st.session_state['modified_data'],st.session_state['sampleRate'], subtype='PCM_16')
        st.session_state['modified_wav_file'] ='tem1.wav'

def spectrogram(data):
    fig =plt.figure(figsize=(8,3))
    plt.specgram(data, Fs=st.session_state.sampleRate,cmap='jet')
    plt.colorbar()
    plt.show()
    return fig 


def draw(data,title,):
        if spectroCheckBox:
            fig =spectrogram(data)
            plt.title(title, 
                fontsize = 8, fontweight ='bold')
            st.pyplot(fig)   
        else:
            time=st.session_state.time
            fig=plt.figure(figsize=(10,2))
            plt.plot(time,data)
            plt.title(title, 
                fontsize = 8, fontweight ='bold')
            st.pyplot(fig)
            


def sound_mode():
    play_buttons()
    
    leftUpColumns,rightUpColumns=st.columns(2)
    with leftUpColumns:
        draw(st.session_state.dataArray,title='Original Signal')
    
    make_sliders()

    if Apply: #sidebar
        apply_action()

    if st.session_state['play_original']: #sidebar
        if pygame.mixer.get_init() is not None:
            pygame.mixer.quit()
        st.session_state['paused']=False    
    with rightUpColumns:
        draw(st.session_state.modified_data,title='Modified Signal')

def draw_medical_signal(data,title):
    time=st.session_state.time
    fig=plt.figure(figsize=(8,3))
    plt.plot(time,data)
    plt.title(title, 
        fontsize = 14, fontweight ='bold')
    fig_html=mpld3.fig_to_html(fig)
    components.html(fig_html,height=300)

def medical_mode():
    magnitude=st.session_state.dataArray.copy()
    maxFreqeuency=st.session_state.maxFrequency
    mainFourierValues=st.session_state.mainFourierValues.copy()
    PPF=int(len(st.session_state.fourierValues)/maxFreqeuency)#points per frequency

    smallFreq=st.slider('x1',min_value=0.,max_value=1.,value=0.5)
    highFreq=st.slider('x2',min_value=0.,max_value=1.,value=0.5)

    fourierValues=st.session_state['fourierValues']
    fourierValues[PPF*130:]=smallFreq*mainFourierValues[PPF*130:]
    fourierValues[PPF*80:PPF*120]=highFreq*mainFourierValues[PPF*80:PPF*120]
    modifiedData=fourier.irfft(fourierValues)

    col1,col2=st.columns(2)
    with col1:
        draw_medical_signal(magnitude,'Real Signal')
    with col2:
        draw_medical_signal(modifiedData,'Modified Signal')    
        


        




def main():
    global file,radio_check,spectroCheckBox,new_dict
    arr=["Frequency","Vowels_Frequency","Music_Instruments","Male Female","Animals"]
    dict={
    "Frequency":{
        "number_of_sliders":10,
        "names_of_sliders":['(0-2205)Hz','(2205-4410)Hz','(4410-6615)Hz','(6615-8820)Hz','(8820-11025)Hz','(11025-13230)Hz','(13230-15435)Hz','(15435-17640)Hz','(17640-19845)HZ','(19845-22050)Hz'],
        "min":[0,2205,4410,6615,8820,11025,13230,15435,17640,19845],
        "max":[2205,4410,6615,8820,11025,13230,15435,17640,19845,22050]
    },
    "Vowels_Frequency":{
        "number_of_sliders":4,
        "names_of_sliders":['sh','r','ou','a'],
        "min":[2000,600,1200,500],
        "max":[7000,3000,5000,2000]
    },
    "Music_Instruments":{
        "number_of_sliders":3,
        "names_of_sliders":['Drums/Piano','Flute','Cymbal'],
        "min":[0,1300,2000],
        "max":[130,2000,22050]
    },
    "Animals":{
        "number_of_sliders":2,
        "names_of_sliders":['Dog/Wolf','Bat/Duck'],
        "min":[170,1300],
        "max":[1300,7500]
    }
    }


    file= st.sidebar.file_uploader("Upload your file",type={"csv",".wav"}, on_change=add_new_uploaded_file,key='uploadedFileCheck')
    spectroCheckBox=st.sidebar.checkbox('Spectrogram')
    radio_check= st.sidebar.radio("choose:",options=arr)
  
    new_dict={}
    if radio_check=="Frequency":
        new_dict.update(dict["Frequency"])
    elif radio_check=="Vowels_Frequency":
        new_dict.update(dict["Vowels_Frequency"])
    elif radio_check=="Music_Instruments":
        new_dict.update(dict["Music_Instruments"])
    elif radio_check=="Animals":
        new_dict.update(dict["Animals"])  
   

    if file is not None:
        if file.type =='audio/wav':
            sound_mode()
        else :
            medical_mode()

main()
