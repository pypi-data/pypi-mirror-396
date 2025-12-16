import string
import datetime as dt

# ---------------------------------------------
# 1. Removing leading or trailing spaces
# ---------------------------------------------

baddata = "   Data Science with too many spaces is bad!!!   "
print("Bad  Data  :", f"'{baddata}'")

cleandata = baddata.strip()
print("Clean Data :", f"'{cleandata}'")



# ---------------------------------------------
# 2. Removing non-printable characters
# ---------------------------------------------

baddata = "Data\x00Science with\x02 funny characters is \x10bad!!!"
print("Bad  Data :", baddata)

cleandata = ''.join(c for c in baddata if c in string.printable)
print("Clean Data:", cleandata)



# ---------------------------------------------
# 3. Reformatting date from YYYY-MM-DD to DD Month YYYY
# ---------------------------------------------


baddate = dt.date(2019, 10, 31)
baddata = baddate.strftime('%Y-%m-%d')  # Convert to string format
print("Bad  Date :", baddata)

gooddate = dt.datetime.strptime(baddata, '%Y-%m-%d')
gooddata = gooddate.strftime('%d %B %Y')
print("Good Date:", gooddata)
print("--------------------------------------------------")
