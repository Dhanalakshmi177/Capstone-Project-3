import easyocr
import streamlit as st
from streamlit_option_menu import option_menu
import mysql.connector as db
import pandas as pd
import os
from PIL import Image
import re
import cv2
import warnings
import matplotlib.pyplot as plt

#------------------------------------------ CONNECTING MYSQL DATABASE

mydb=db.connect(
    host="localhost",
    port="3306",
    user="root",
    password="root",
    database="bizcard"
)
mycursor=mydb.cursor()

# --------------------------------------------------Logo & details on top

icon = Image.open("b.png")
st.set_page_config(page_title= "BizCardX-Extracting Business Card Data with OCR | By Dhanalakshmi S",
                   page_icon= icon,
                   layout= "wide",
                   initial_sidebar_state= "expanded")
               
# ----------------------------------------------------------------to fetch data from image

reader = easyocr.Reader(['en'],gpu=False)          # EASY OCR

# ---------------------------------------------------------------------TABLE CREATION

query='''CREATE TABLE IF NOT EXISTS card_data
                (Card_Holder_Name TEXT,
                    Designation TEXT,
                    Company_Name TEXT,
                    Phone_Number VARCHAR(50),
                    Email TEXT,
                    Website TEXT,
                    Area VARCHAR(50), 
                    City TEXT,
                    State TEXT,
                    Pincode VARCHAR(10),
                    Image LONGBLOB
                    )'''
mycursor.execute(query)
mydb.commit()

# --------------------------------------MENU
 
st.markdown("<div style='text-align: center; color:skyblue; font-weight:bold;font-style: italic; font-size: 106px;'>BizCardX</div><div style='text-align: center;font-style:italic; font-size: 54px;'>Extracting Business Card Data with OCR</div>", unsafe_allow_html=True)
     
opt = option_menu(menu_title=None,
                  options=['Home','Data Extraction','Modify'],
                icons=["house","cloud-upload","pencil"],
                #menu_icon="pe.png",
                default_index=0,
                orientation='horizontal',
                styles={"nav-link": {"font-size": "20px", "text-align": "left", "margin": "-2px", "--hover-color": "#FCE5CD"},
                        "nav-link-selected": {"background-color": "#CFE2F3"}})

#------------------------------------HOME
if opt=="Home":
   
        st.write(" ") 
        st.markdown("### :blue[OVERVIEW ]")
        st.markdown("### This Python application designed to extract text information from business cards. The main purpose of BizcardX is to automate the process of extracting key details from business card images such as the name, designation, company, contact information and other relevant data. By leveraging the power of OCR (Optical Character Recognition) provided by EasyOCR.")
        col1,col2=st.columns([3,2],gap="small")
        with col1:
            st.markdown("""
                        ### :blue[TECHNOLOGIES USED ]                  
                        ###     PYTHON
                        ###  OPTICAL CHARACTER RECOGNITION (OCR)
                        ### PANDAS
                        ### MYSQL
                        ### STREAMLIT GUI
            
                        """)
        with col2:
              st.write(" ")
              st.image("dnxky.png",caption=' BizcardX', use_column_width=True)
           
        #st.write(" ")
        #st.write(" ")
        #st.markdown("### :blue[Wanna Take a Look @ DB , Click Here Below !]")
        #if st.button(" SHOW DATABASE"):
           # mycursor.execute('''Select Card_Holder_Name,Designation,Company_Name,
                   # Phone_Number,Email,Website,Area,City,State,Pincode from card_data''')
            #updated_df = pd.DataFrame(mycursor.fetchall(),
                        #columns=["Card Holder Name","Designation","Company Name",
                       # "#Phone Number", "Email","Website", "Area", "City", "State", "Pin_Code"])
            #st.write(updated_df)
        
    # ------------------------------ UPLOAD IMAGE & EXTRACT DATA
if opt=="Data Extraction":
  
    image_files = st.file_uploader("Upload the Business Card below:", type=["png","jpg","jpeg"])
    def save_card(image_files):
        uploaded_cards_dir = os.path.join(os.getcwd(),"bizcard")
        with open(os.path.join(uploaded_cards_dir, image_files.name), "wb") as f:
            f.write(image_files.getbuffer())

#-------------------------------------------------------UPLOADING BIZCARD
    if image_files != None:
        col1, col2 = st.columns(2, gap="large")
        with col1:
            img = image_files.read()
            st.markdown("### BizCard Uploaded")
            st.image(img, caption=' ',width=650)
            save_card(image_files)
#------------------------------------------------------------EXTRACTION PROCESS FROM IMAGE

        with col2:
            saved_img = os.getcwd() + "\\" "\\" + image_files.name
            image = cv2.imread(saved_img)
            res = reader.readtext(saved_img)
            st.markdown("### Extracting Data from Bizcard")
            def image_preview(image, res):
                for (bbox, text, prob) in res:
                    # unpack the bounding box
                    (tl, tr, br, bl) = bbox
                    tl = (int(tl[0]), int(tl[1]))
                    tr = (int(tr[0]), int(tr[1]))
                    br = (int(br[0]), int(br[1]))
                    bl = (int(bl[0]), int(bl[1]))
                    cv2.rectangle(image, tl, br, (0, 255, 0), 2)
                    cv2.putText(image, text, (tl[0], tl[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                plt.rcParams['figure.figsize'] = (15, 15)
                plt.axis('off')
                plt.imshow(image)
            b=image_preview(image, res)
            st.set_option('deprecation.showPyplotGlobalUse', False)
            warnings.filterwarnings("ignore", category=DeprecationWarning)   # remove if error throws
            st.pyplot(b)

        saved_img = os.getcwd() + "\\" "\\" + image_files.name
        result = reader.readtext(saved_img, detail=0, paragraph=False)
        
#----------------------------------------------------------- CONVERTING IMAGE TO BINARY 
        def img_to_binary(file):
            with open(file, 'rb') as file:
                binaryData = file.read()
            return binaryData
        
#------------------------------------ FETCHING SPECIFIC DATA FOR CORRESPONDING COLUMNS
        
       
        data = {
               "Card_Holder_Name":[],
                "Designation":[],
                "Company_Name":[],
                "Phone_Number":[],
                "Email":[],
                "Website":[],
                "Area":[],
                "City":[],
                "State":[],
                "Pincode":[],
                "image": img_to_binary(saved_img)
                }

        def get_data(res):
            for j, i in enumerate(res):
                
                # -------------------------------------------------WEBSITE
                if "www" in i or "Www" in i or "wwW." in i or "WWW" in i :
                    data["Website"].append(i)
                

                # ---------------------------------------------------EMAIL 
                elif "@" in i:
                    data["Email"].append(i)
                    
                # --------------------------------------------------CONTACT
                elif "-" in i:
                    data["Phone_Number"].append(i)
                    if len(data["Phone_Number"]) == 2:
                        data["Phone_Number"] = " & ".join(data["Phone_Number"])


                        
                #  -----------------------------------------COMPANY NAME

                elif j == len(res) - 1:
                    data["Company_Name"].append(i)
                    if len(data["Company_Name"])==2:
                            data["Company_Name"]=" & ".join(data["Company_Name"])
                              



                    # ----------------------------------------CARD HOLDER NAME
                elif j == 0:
                        data["Card_Holder_Name"].append(i)
                        
                    #  ----------------------------------------DESIGNATION
                elif j == 1:
                        data["Designation"].append(i)
                        
                    # ------------------------------------------------ AREA
                if re.findall('^[0-9].+, [a-zA-Z]+', i):
                        data["Area"].append(i.split(',')[0])
                elif re.findall('[0-9] [a-zA-Z]+', i):
                        data["Area"].append(i)
                    
                    # --------------------------------------CITY 
                match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
                match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
                match3 = re.findall('^[E].*', i)
                if match1:
                        data["City"].append(match1[0])
                elif match2:
                        data["City"].append(match2[0])
                elif match3:
                        data["City"].append(match3[0])
                        
                    # -------------------------------------------- STATE
                state_match = re.findall('[a-zA-Z]{9} +[0-9]', i)
                if state_match:
                    data["State"].append(i[:9])
                elif re.findall('^[0-9].+, ([a-zA-Z]+);', i):
                    data["State"].append(i.split()[-1])
                if len(data["State"]) == 2:
                    data["State"].pop(0)

                # -------------------------------------------------PINCODE
                if len(i) >= 6 and i.isdigit():
                    data["Pincode"].append(i)
                elif re.findall('[a-zA-Z]{9} +[0-9]', i):
                    data["Pincode"].append(i[10:])
        get_data(result)
        df = pd.DataFrame(data)
        st.success(" :rainbow[TEXT IS EXTRACTED SUCCESSFULLY ]:green[✅]")         # -----------------EXTRACTION SUCCESSFULL
        st.write(df)
               
#-----------------------------------------------------------UPLOAD TO DB

        if st.button("Upload to Database"):
            for i, row in df.iterrows():
                query1='''insert into card_data(Card_Holder_Name,Designation,Company_Name,
                Phone_Number,Email,Website,Area,City,State,Pincode,Image)
                values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                mycursor.execute(query1, tuple(row))
                mydb.commit()
                mycursor.execute('''Select Card_Holder_Name,Designation,Company_Name,
                Phone_Number,Email,Website,Area,City,State,Pincode from card_data''')
                updated_df = pd.DataFrame(mycursor.fetchall(),
                columns=["Card Holder Name","Designation","Company Name",
                "Phone Number", "Email","Website", "Area", "City", "State", "Pin_Code"])
                st.success(" :rainbow[ UPLOADED SUCCESSFULLY]:green[✅]")
                st.write(updated_df)

#-------------------------------------------------MODIFYING


if opt=="Modify":
    tab1,tab2=st.tabs(["**EDIT**","**DELETE**"])
# ---------------------------------------------------------------------- EDIT 

    with tab1:

            st.markdown("***:violet[ You can EDIT your data over here ]***")
            try:
                    mycursor.execute("SELECT Card_Holder_Name FROM card_data")
                    result = mycursor.fetchall()
                    business_cards = {}
                    for row in result:
                        business_cards[row[0]] = row[0]
                    options = ["Select Card"] + list(business_cards.keys())
                    selected_card = st.selectbox("**Pick a card**", options)
                    if selected_card == "Select Card":
                        st.write("Card not selected yet")
                    else:
                        st.markdown("#### Edit or Update the Data ")
                        mycursor.execute('''Select Card_Holder_Name,Designation,Company_Name,
                        Phone_Number,Email,Website,Area,City,State,Pincode from card_data WHERE Card_Holder_Name=%s''',
                        (selected_card,))
                        result = mycursor.fetchone()

                        # DISPLAYING ALL THE INFOS

                        company_name = st.text_input("Company_Name", result[2])
                        card_holder = st.text_input("Card_Holder", result[0])
                        designation = st.text_input("Designation", result[1])
                        mobile_number = st.text_input("Mobile_Number", result[3])
                        email = st.text_input("Email", result[4])
                        website = st.text_input("Website", result[5])
                        area = st.text_input("Area", result[6])
                        city = st.text_input("City", result[7])
                        state = st.text_input("State", result[8])
                        pin_code = st.text_input("Pin_Code", result[9])

                        if st.button(":black[SAVE CHANGES]"):

                                sql_update_query = """
                                        UPDATE card_data 
                                        SET 
                                            Card_Holder_Name=%s, 
                                            Designation=%s, 
                                            Company_Name=%s, 
                                            Phone_Number=%s, 
                                            Email=%s, 
                                            Website=%s,
                                            Area=%s, 
                                            City=%s, 
                                            State=%s, 
                                            Pincode=%s 
                                        WHERE 
                                            Card_Holder_Name=%s
                                    """

                                data_tuple = (
                                    card_holder,
                                    designation,
                                    company_name,
                                    mobile_number,
                                    email,
                                    website,
                                    area,
                                    city,
                                    state,
                                    pin_code,
                                    selected_card
                                )

                                try:
                                    mycursor.execute(sql_update_query,data_tuple)
                                    mydb.commit()
                                    st.success(":rainbow[RECORD UPDATED SUCCESSFULLY]")

                                except Exception as e:
                                            print("Error occurred:", e)
                                            #mydb.rollback()  # rollback on error

                        if st.button(":black[VIEW DB]"):
                                        mycursor.execute('''Select Card_Holder_Name,Designation,Company_Name,
                                                Phone_Number,Email,Website,Area,City,State,Pincode from card_data''')
                                        updated_df = pd.DataFrame(mycursor.fetchall(),
                                                    columns=["Card Holder Name","Designation","Company Name",
                                                    "Phone Number", "Email","Website", "Area", "City", "State", "Pin_Code"])
                                        st.write(updated_df)
                            
            except:
                 st.warning("Oops! No Data Found")


#---------------------------------------------------------DELETE            
    with tab2:
            st.subheader("*:violet[Delete Data]*")
            try:
                    mycursor.execute("SELECT Card_Holder_Name FROM card_data")
                    result = mycursor.fetchall()
                    business_cards = {}
                    for row in result:
                        business_cards[row[0]] = row[0]
                    options = ["None"] + list(business_cards.keys())
                    selected_card = st.selectbox("**Pick a card**", options)
                    if selected_card == "None":
                        st.write("No card selected yet")
                    else:
                        st.write(f"### :green[**{selected_card}'s**] Card Has Been Selected to Delete")
                        if st.button("Please Confirm"):
                            mycursor.execute(f"DELETE FROM card_data WHERE Card_Holder_Name='{selected_card}'")
                            mydb.commit()
                            st.success(":rainbow[Bizcard Deleted Successfully]")
                    
                    if st.button(":black[SHOW DB]"):
                                mycursor.execute('''Select Card_Holder_Name,Designation,Company_Name,
                                    Phone_Number,Email,Website,Area,City,State,Pincode from card_data''')
                                updated_df3 = pd.DataFrame(mycursor.fetchall(),
                                                            columns=["Card_Holder_Name","Designation","Company_Name",
                                    "Phone_Number","Email","Website","Area","City","State","Pincode"])
                                st.write(updated_df3)
            except:
                       pass
                          #st.warning("There is no data available in the database")