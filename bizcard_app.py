
import numpy as np
import pandas as pd
import streamlit as st
import easyocr
from PIL import Image
import re
import io
import sqlite3

def img_text(filepath):

  inp_img = Image.open(filepath)

  img_arr = np.array(inp_img)    # converting image to array

  reader = easyocr.Reader(["en"])    # Specifying langauge

  txt = reader.readtext(img_arr, detail = 0)

  return txt, inp_img

def text_extraction(text):

  text_values = {"NAME":[], "DESIGNATION":[], "COMPANY_NAME":[], "CONTACT":[], "EMAIL":[], "WEBSITE":[], "ADDRESS":[], "PINCODE":[]}

  text_values["NAME"].append(text[0])
  text_values["DESIGNATION"].append(text[1])

  for i in range(2, len(text)):

    if text[i].startswith("+") or (text[i].replace("-","").isdigit and "-" in text[i]):
      text_values["CONTACT"].append(text[i])

    elif "@" in text[i] and ".com" in text[i]:
      text_values["EMAIL"].append(text[i])

    elif "WWW" in text[i] or "WWW" in text[i] or "Www" in text[i] or "wWw" in text[i] or "wwW" in text[i]:
      lowercase = text[i].lower()
      text_values["WEBSITE"].append(lowercase)

    elif "Tamil Nadu" in text[i] or "TamilNadu" in text[i] or text[i].isdigit():
      text_values["PINCODE"].append(text[i])

    elif re.match('^[A-Za-z]', text[i]):
      text_values["COMPANY_NAME"].append(text[i])

    else :
      address = re.sub(r'[,;]','',text[i])
      text_values["ADDRESS"].append(address)

  for key, value in text_values.items():
    if len(value)>0:
      concat = " ".join(value)
      text_values[key] = [concat]

    else:
      values = "NA"
      text_values[key] = [values]

  return text_values


# STREAMLIT

st.set_page_config(layout = "wide")
st.title(":green[BIZCARD DATA EXTRACTION]")

with st.sidebar:
  option = st.selectbox(":blue[MAIN MENU]", options= ["Upload & Modify", "Delete"])

if option == "Upload & Modify":
  img = st.file_uploader(":rainbow[UPLOAD IMAGE]", type = ["png", "jpg", "jpeg"])

  if img is not None:
    st.image(img, width = 300)

    text_image, input_image = img_text(img)

    text_dict = text_extraction(text_image)

    if text_dict:
      st.success("Text Extracted successfully")

    df = pd.DataFrame(text_dict)

    # CONVERTING IMAGE TO BYTES

    image_bytes = io.BytesIO()
    input_image.save(image_bytes, format = "PNG")

    image_data = image_bytes.getvalue()

    # CREATING DICTIONARY
    data = {"IMAGE": [image_data]}

    df1 = pd.DataFrame(data)

    new_df = pd.concat([df, df1], axis = 1)

    st.dataframe(new_df)

    button_1 = st.button("UPLOAD", use_container_width = True)

    if button_1:

      mydb = sqlite3.connect("bizcardx.db")
      cursor = mydb.cursor()

      # TABLE CREATION

      tab_query = '''CREATE TABLE IF NOT EXISTS bizcard_details(name varchar(255),
                                                                designation varchar(255),
                                                                company_name varchar(255),
                                                                contact varchar(255),
                                                                email varchar(255),
                                                                website text,
                                                                address text,
                                                                pincode varchar(255),
                                                                image text)'''

      cursor.execute(tab_query)
      mydb.commit()

      # INSERT QUERY

      insert_query = '''INSERT INTO bizcard_details(name, designation, company_name, contact,
                                                    email, website, address, pincode, image)

                                                    values(?,?,?,?,?,?,?,?,?)'''

      datas = new_df.values.tolist()
      cursor.execute(insert_query, datas[0])
      mydb.commit()

      st.success("SAVED SUCESSFULLY")

  method = st.selectbox(":rainbow[SELECT THE METHOD]", options = ["preview", "Modify"], index = None, placeholder = "Choose anyone Method")

  if method == "preview":

    mydb = sqlite3.connect("bizcardx.db")
    cursor = mydb.cursor()

    #SELECT QUERY

    select_query = "SELECT * FROM bizcard_details"

    cursor.execute(select_query)

    table = cursor.fetchall()

    mydb.commit()

    table_df = pd.DataFrame(table, columns = ("NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE",
                                              "ADDRESS", "PINCODE", "IMAGE"))
    st.dataframe(table_df)

  elif method == "Modify":

    mydb = sqlite3.connect("bizcardx.db")
    cursor = mydb.cursor()

    #SELECT QUERY

    select_query = "SELECT * FROM bizcard_details"

    cursor.execute(select_query)

    table = cursor.fetchall()

    mydb.commit()

    table_df = pd.DataFrame(table, columns = ("NAME", "DESIGNATION", "COMPANY_NAME", "CONTACT", "EMAIL", "WEBSITE",
                                              "ADDRESS", "PINCODE", "IMAGE"))
    colm1, colm2 = st.columns(2)

    with colm1:
      sn = st.selectbox(":rainbow[SELECT THE NAME]", table_df["NAME"])

    df3 = table_df[table_df["NAME"] == sn]

    df4 = df3.copy()

    col1, col2 = st.columns(2)

    with col1:
      m_name = st.text_input("NAME", df3["NAME"].unique()[0])
      m_desig = st.text_input("DESIGNATION", df3["DESIGNATION"].unique()[0])
      m_co_name = st.text_input("COMPANY_NAME", df3["COMPANY_NAME"].unique()[0])
      m_cont = st.text_input("CONTACT", df3["CONTACT"].unique()[0])
      m_email = st.text_input("EMAIL", df3["EMAIL"].unique()[0])

      df4["NAME"] = m_name
      df4["DESIGNATION"] = m_desig
      df4["COMPANY_NAME"] = m_co_name
      df4["CONTACT"] = m_cont
      df4["EMAIL"] = m_email

    with col2:
      m_website = st.text_input("WEBSITE", df3["WEBSITE"].unique()[0])
      m_address = st.text_input("ADDRESS", df3["ADDRESS"].unique()[0])
      m_pincode = st.text_input("PINCODE", df3["PINCODE"].unique()[0])
      m_image = st.text_input("IMAGE", df3["IMAGE"].unique()[0])

      df4["WEBSITE"] = m_website
      df4["ADDRESS"] = m_address
      df4["PINCODE"] = m_pincode
      df4["IMAGE"] = m_image


    st.dataframe(df4)

    coll1, coll2 = st.columns(2)

    with coll1:
      button_2 = st.button("Modify", use_container_width = True)

    if button_2:
      mydb = sqlite3.connect("bizcardx.db")
      cursor = mydb.cursor()

      cursor.execute(f"DELETE FROM bizcard_details WHERE NAME = '{sn}'")
      mydb.commit()

      insert_query = '''INSERT INTO bizcard_details(name, designation, company_name, contact,
                                                    email, website, address, pincode, image)

                                                    values(?,?,?,?,?,?,?,?,?)'''

      datas = df4.values.tolist()
      cursor.execute(insert_query, datas[0])
      mydb.commit()

      st.success("MODIFIED SUCESSFULLY")

elif option == "Delete":
    mydb = sqlite3.connect("bizcardx.db")
    cursor = mydb.cursor()

    col1, col2 = st.columns(2)

    with col1:

      select_query = "SELECT NAME FROM bizcard_details"

      cursor.execute(select_query)

      table1 = cursor.fetchall()

      mydb.commit()

      names = []

      for i in table1:
        names.append(i[0])

      ns = st.selectbox(":rainbow[SELECT THE NAME]", names)


    with col2:

      select_query = f"SELECT DESIGNATION FROM bizcard_details WHERE NAME = '{ns}'"

      cursor.execute(select_query)

      table2 = cursor.fetchall()

      mydb.commit()

      designation = []

      for j in table2:
        designation.append(j[0])

      ds = st.selectbox(":rainbow[SELECT THE DESIGNATION]", designation)

    if ns and ds:
      col1, col2 = st.columns(2)

      with col1:

        st.write(f":green[Selected Name] : {ns} ")
        
      with col2:
        st.write(f":green[Selected Designation] : {ds}")

      remove = st.button("DELETE", use_container_width = True)

      if remove:

        cursor.execute(f"DELETE FROM bizcard_details WHERE NAME ='{ns}' and DESIGNATION = '{ds}'")

        mydb.commit()

        st.warning("DELETED")

  
