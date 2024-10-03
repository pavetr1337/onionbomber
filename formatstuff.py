# FORMATTING FROM 7XXXXXXXXXX

# phone = "71234567890"

# +7 (123) 456-78-90
def format_wide(ph):
    return f"+{ph[0]} ({ph[1:4]}) {ph[4:7]}-{ph[7:9]}-{ph[9:11]}"

# +7(123)-456-78-90
def format_wide1(ph):
    return f"+{ph[0]}({ph[1:4]})-{ph[4:7]}-{ph[7:9]}-{ph[9:11]}"

# %2B7+(123)+456-7890 creepy shit
def format_strange(ph):
    return f"%2B{ph[0]}+({ph[1:4]})+{ph[4:7]}-{ph[7:11]}"

# +7+(123)+456-78-90 creepy shit
def format_strange2(ph):
    return f"+{ph[0]}+({ph[1:4]})+{ph[4:7]}-{ph[7:9]}-{ph[9:11]}"

# print(format_strange2(phone))