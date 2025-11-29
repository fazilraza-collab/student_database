import streamlit as st
import mysql.connector
import pandas as pd
from datetime import datetime, date

# ========== DB CONFIG (YAHAN APNA CHANGE KARO) ==========
DB_HOST = "localhost"
DB_USER = "root"              # ← apna MySQL user
DB_PASSWORD = "fazilraza" # ← apna MySQL password
DB_NAME = "students"          # ← apna database name


# ========== DB CONNECTION & HELPERS ==========
@st.cache_resource
def get_connection():
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )


def run_query(query, params=None):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute(query, params or ())
    rows = cur.fetchall()
    cur.close()
    return rows


def run_execute(query, params=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params or ())
    conn.commit()
    cur.close()


@st.cache_data
def get_table_df(table_name: str) -> pd.DataFrame:
    conn = get_connection()
    df = pd.read_sql(f"SELECT * FROM `{table_name}`;", conn)
    return df


@st.cache_data
def get_all_tables() -> list:
    """Return all table names from current DB."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SHOW TABLES;")
    tables = [row[0] for row in cur.fetchall()]
    cur.close()
    return tables


# ====== UI CONFIG ======
st.set_page_config(page_title="Coaching ERP Dashboard", layout="wide")
st.title("🎓 Coaching Management – Streamlit ERP")
st.caption(f"Connected to MySQL database: **{DB_NAME}**")

# ====== SIDEBAR NAVIGATION ======
pages = [
    "Dashboard",
    "Students",
    "Courses",
    "Attendance",
    "Fees",
    "Leads",
    "Results",
    "Faculty & Classes",
    "Rooms Utilization",
    "All Tables"
]

st.sidebar.header("📂 Modules")
page = st.sidebar.radio("Go to:", pages)


# ================== 1. DASHBOARD ==================
if page == "Dashboard":
    st.subheader("📊 Overall Analytics Dashboard")

    col1, col2, col3, col4 = st.columns(4)

    # KPIs
    try:
        total_students = run_query("SELECT COUNT(*) AS c FROM student;")[0]["c"]
    except:
        total_students = 0

    try:
        total_courses = run_query("SELECT COUNT(*) AS c FROM course WHERE STATUS='Active';")[0]["c"]
    except:
        total_courses = 0

    try:
        total_leads = run_query("SELECT COUNT(*) AS c FROM lead;")[0]["c"]
    except:
        total_leads = 0

    try:
        total_fee_paid = run_query("SELECT IFNULL(SUM(AMOUNT_PAID),0) AS s FROM fee_payment;")[0]["s"]
    except:
        total_fee_paid = 0

    with col1:
        st.metric("Total Students", total_students)
    with col2:
        st.metric("Active Courses", total_courses)
    with col3:
        st.metric("Total Leads", total_leads)
    with col4:
        st.metric("Total Fees Collected", f"₹ {total_fee_paid:,.0f}")

    st.write("---")

    # Course-wise student count USING student.COURSE_NAME
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 👥 Course-wise Student Count")
        try:
            rows = run_query("""
                SELECT 
                    s.COURSE_NAME,
                    COUNT(s.STUDENT_ID) AS student_count
                FROM student s
                GROUP BY s.COURSE_NAME
                ORDER BY student_count DESC;
            """)
            if rows:
                df = pd.DataFrame(rows)
                df = df.set_index("COURSE_NAME")
                st.bar_chart(df["student_count"])
            else:
                st.info("No student/course data found.")
        except Exception as e:
            st.error(f"Error loading course-wise count: {e}")

    # Monthly fee collection
    with col_b:
        st.markdown("#### 💰 Monthly Fee Collection")
        try:
            rows = run_query("""
                SELECT DATE_FORMAT(PAYMENT_DATE, '%Y-%m') AS ym,
                       SUM(AMOUNT_PAID) AS total_paid
                FROM fee_payment
                GROUP BY ym
                ORDER BY ym;
            """)
            if rows:
                df = pd.DataFrame(rows)
                df = df.set_index("ym")
                st.line_chart(df["total_paid"])
            else:
                st.info("No fee payment data found.")
        except Exception as e:
            st.error(f"Error loading fee data: {e}")

    st.write("---")

    # Lead status distribution
    st.markdown("#### 📞 Lead Status Distribution")
    try:
        rows = run_query("""
            SELECT STATUS, COUNT(*) AS count
            FROM lead
            GROUP BY STATUS;
        """)
        if rows:
            df = pd.DataFrame(rows)
            df = df.set_index("STATUS")
            st.bar_chart(df["count"])
        else:
            st.info("No lead data found.")
    except Exception as e:
        st.error(f"Error loading lead status data: {e}")


# ================== 2. STUDENTS ==================
elif page == "Students":
    st.subheader("🎓 Student Management")

    try:
        df = get_table_df("student")
    except Exception as e:
        st.error(f"Error loading student table: {e}")
        df = pd.DataFrame()

    if not df.empty:
        # Filter by COURSE_NAME
        if "COURSE_NAME" in df.columns:
            unique_courses = sorted(df["COURSE_NAME"].dropna().unique())
            course_filter = st.selectbox(
                "Filter by COURSE_NAME (optional):",
                options=["All"] + list(unique_courses),
                index=0
            )
            if course_filter != "All":
                df = df[df["COURSE_NAME"] == course_filter]

        # Status filter
        if "STATUS" in df.columns:
            status_values = sorted(df["STATUS"].dropna().unique())
            status_filter = st.selectbox(
                "Filter by STATUS:",
                options=["All"] + list(status_values),
                index=0
            )
            if status_filter != "All":
                df = df[df["STATUS"] == status_filter]

        st.caption(f"Showing {len(df)} students")
        st.dataframe(df, use_container_width=True)

        st.write("---")

        # ➕ Add New Student
        with st.expander("➕ Add New Student"):
            with st.form("add_student_form"):
                name = st.text_input("Name *")
                gender = st.text_input("Gender")
                dob = st.date_input("DOB", value=date(2005, 1, 1))
                mobile = st.text_input("Mobile")
                email = st.text_input("Email ID")
                address = st.text_area("Address")
                city = st.text_input("City")
                state = st.text_input("State")
                pincode = st.text_input("Pincode")
                parent_name = st.text_input("Parent Name")
                parent_mobile = st.text_input("Parent Mobile")
                course_name = st.text_input("COURSE_NAME * (e.g. JEE Main Batch, NEET Batch)")
                join_date = st.date_input("Join Date", value=date.today())
                status = st.text_input("Status", value="Active")

                submitted = st.form_submit_button("Add Student")

                if submitted:
                    if not name or not course_name:
                        st.error("Name and COURSE_NAME are required.")
                    else:
                        try:
                            run_execute("""
                                INSERT INTO student
                                (NAME, GENDER, DOB, MOBILE, EMAIL_ID, ADDRESS, CITY, STATE, PINCODE,
                                 PARENT_NAME, PARENT_MOBILE, COURSE_NAME, JOIN_DATE, STATUS)
                                VALUES
                                (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);
                            """, (
                                name, gender, dob, mobile, email, address, city, state, pincode,
                                parent_name, parent_mobile, course_name, join_date, status
                            ))
                            st.success("Student added successfully.")
                            st.cache_data.clear()
                        except Exception as e:
                            st.error(f"Error inserting student: {e}")

        # ✏️ Update status
        with st.expander("✏️ Update Student Status"):
            sid = st.text_input("Enter STUDENT_ID to update:")
            new_status = st.text_input("New STATUS value (e.g. Active / Inactive)")
            if st.button("Update Status"):
                if sid and new_status:
                    try:
                        run_execute(
                            "UPDATE student SET STATUS = %s WHERE STUDENT_ID = %s;",
                            (new_status, sid)
                        )
                        st.success(f"Student {sid} status updated.")
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"Error updating status: {e}")
                else:
                    st.warning("Enter both STUDENT_ID and STATUS.")

        # 🗑️ Delete
        with st.expander("🗑️ Delete Student"):
            del_id = st.text_input("Enter STUDENT_ID to delete:")
            if st.button("Delete Student"):
                if del_id:
                    try:
                        run_execute("DELETE FROM student WHERE STUDENT_ID = %s;", (del_id,))
                        st.success(f"Student {del_id} deleted (if existed).")
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"Error deleting student: {e}")
                else:
                    st.warning("Enter a valid STUDENT_ID.")

        # Course-wise chart using COURSE_NAME
        st.write("---")
        st.markdown("#### 📊 Course-wise Student Count")
        try:
            rows = run_query("""
                SELECT COURSE_NAME, COUNT(*) AS student_count
                FROM student
                GROUP BY COURSE_NAME
                ORDER BY student_count DESC;
            """)
            if rows:
                dfc = pd.DataFrame(rows).set_index("COURSE_NAME")
                st.bar_chart(dfc["student_count"])
            else:
                st.info("No students found for chart.")
        except Exception as e:
            st.error(f"Error loading course-wise student chart: {e}")
    else:
        st.info("Student table is empty or not accessible.")


# ================== 3. COURSES ==================
elif page == "Courses":
    st.subheader("📚 Course Management")

    try:
        df = get_table_df("course")
    except Exception as e:
        st.error(f"Error loading course table: {e}")
        df = pd.DataFrame()

    if not df.empty:
        # Status filter
        if "STATUS" in df.columns:
            st_vals = sorted(df["STATUS"].dropna().unique())
            st_filter = st.selectbox(
                "Filter by STATUS:",
                options=["All"] + list(st_vals),
                index=0
            )
            if st_filter != "All":
                df = df[df["STATUS"] == st_filter]

        st.caption(f"Showing {len(df)} courses")
        st.dataframe(df, use_container_width=True)

        st.write("---")

        # Add new course
        with st.expander("➕ Add New Course"):
            with st.form("add_course_form"):
                cname = st.text_input("COURSE_NAME *")
                category = st.text_input("CATEGORY (e.g. JEE, NEET, Board)")
                duration = st.number_input("DURATION_MONTHS", min_value=1, step=1)
                fees = st.number_input("FEES", min_value=0.0, step=1000.0)
                level = st.text_input("LEVEL (e.g. Foundation, Regular, Crash)")
                status = st.text_input("STATUS", value="Active")

                sub_course = st.form_submit_button("Add Course")

                if sub_course:
                    if not cname:
                        st.error("COURSE_NAME is required.")
                    else:
                        try:
                            run_execute("""
                                INSERT INTO course
                                (COURSE_NAME, CATEGORY, DURATION_MONTHS, FEES, LEVEL, STATUS)
                                VALUES (%s,%s,%s,%s,%s,%s);
                            """, (cname, category, duration, fees, level, status))
                            st.success("Course added successfully.")
                            st.cache_data.clear()
                        except Exception as e:
                            st.error(f"Error inserting course: {e}")

        # Update course status
        with st.expander("✏️ Update Course Status"):
            cid = st.text_input("Enter COURSE_ID to update:")
            new_status = st.text_input("New STATUS (Active/Inactive):")
            if st.button("Update Course Status"):
                if cid and new_status:
                    try:
                        run_execute(
                            "UPDATE course SET STATUS = %s WHERE COURSE_ID = %s;",
                            (new_status, cid)
                        )
                        st.success(f"Course {cid} status updated.")
                        st.cache_data.clear()
                    except Exception as e:
                        st.error(f"Error updating course: {e}")
                else:
                    st.warning("Enter both COURSE_ID and STATUS.")

        # Fee summary by course (from fee_payment)
        st.write("---")
        st.markdown("#### 💰 Fee Collection by Course")
        try:
            rows = run_query("""
                SELECT 
                    c.COURSE_NAME,
                    SUM(c.FEES) AS total_course_fees, 
                    IFNULL(SUM(fp.AMOUNT_PAID),0) AS total_paid
                FROM course c
                LEFT JOIN fee_payment fp ON fp.COURSE_ID = c.COURSE_ID
                GROUP BY c.COURSE_NAME;
            """)
            if rows:
                df_fee = pd.DataFrame(rows).set_index("COURSE_NAME")
                st.bar_chart(df_fee[["total_course_fees", "total_paid"]])
            else:
                st.info("No fee data available for courses.")
        except Exception as e:
            st.error(f"Error loading course fee chart: {e}")

    else:
        st.info("Course table is empty or not accessible.")


# ================== 4. ATTENDANCE ==================
elif page == "Attendance":
    st.subheader("📅 Attendance Analytics")

    try:
        df = get_table_df("attendance")
    except Exception as e:
        st.error(f"Error loading attendance table: {e}")
        df = pd.DataFrame()

    if not df.empty:
        # Filter by STUDENT_ID
        if "STUDENT_ID" in df.columns:
            sid_values = sorted(df["STUDENT_ID"].dropna().unique())
            sid = st.selectbox(
                "Filter by STUDENT_ID (optional):",
                options=["All"] + list(sid_values),
                index=0
            )
            if sid != "All":
                df = df[df["STUDENT_ID"] == sid]

        # Date range filter
        if "ATTENDANCE_DATE" in df.columns:
            df["ATTENDANCE_DATE"] = pd.to_datetime(df["ATTENDANCE_DATE"])
            min_date, max_date = df["ATTENDANCE_DATE"].min(), df["ATTENDANCE_DATE"].max()
            date_range = st.date_input("Date range:", [min_date, max_date])
            if len(date_range) == 2:
                start, end = date_range
                df = df[(df["ATTENDANCE_DATE"] >= pd.to_datetime(start)) &
                        (df["ATTENDANCE_DATE"] <= pd.to_datetime(end))]

        st.caption(f"Showing {len(df)} attendance rows")
        st.dataframe(df, use_container_width=True)

        # Present trend chart
        if "ATTENDANCE_DATE" in df.columns and "STATUS" in df.columns:
            st.markdown("#### 📈 Daily Present Count")
            try:
                pres = df[df["STATUS"] == "Present"]
                if not pres.empty:
                    daily = pres.groupby("ATTENDANCE_DATE").size().reset_index(name="present_count")
                    daily = daily.set_index("ATTENDANCE_DATE")
                    st.line_chart(daily["present_count"])
                else:
                    st.info("No 'Present' records to show trend.")
            except Exception as e:
                st.error(f"Error plotting attendance chart: {e}")
    else:
        st.info("Attendance table is empty or not accessible.")


# ================== 5. FEES ==================
elif page == "Fees":
    st.subheader("💰 Fee Management Dashboard")

    # Join via fee_payment → course → student
    try:
        rows = run_query("""
            SELECT 
                s.STUDENT_ID,
                s.NAME,
                c.COURSE_NAME,
                c.FEES AS total_fees,
                IFNULL(SUM(fp.AMOUNT_PAID),0) AS total_paid,
                (c.FEES - IFNULL(SUM(fp.AMOUNT_PAID),0)) AS balance
            FROM fee_payment fp
            JOIN student s ON fp.STUDENT_ID = s.STUDENT_ID
            JOIN course c   ON fp.COURSE_ID = c.COURSE_ID
            GROUP BY s.STUDENT_ID, s.NAME, c.COURSE_NAME, c.FEES
            ORDER BY s.STUDENT_ID;
        """)
        df = pd.DataFrame(rows)
    except Exception as e:
        st.error(f"Error loading fee summary: {e}")
        df = pd.DataFrame()

    if not df.empty:
        st.caption(f"Total students in fee summary: {len(df)}")

        pending_only = st.checkbox("Show only students with pending balance > 0", value=False)
        if pending_only:
            df = df[df["balance"] > 0]

        st.dataframe(df, use_container_width=True)

        # Course-wise fee chart
        st.markdown("#### 📊 Course-wise Fee Collection")
        try:
            course_fee = df.groupby("COURSE_NAME")[["total_fees", "total_paid"]].sum()
            st.bar_chart(course_fee)
        except Exception as e:
            st.error(f"Error plotting course fee chart: {e}")
    else:
        st.info("No fee summary available.")


# ================== 6. LEADS ==================
elif page == "Leads":
    st.subheader("📞 Lead Management & Analytics")

    try:
        df = get_table_df("lead")
    except Exception as e:
        st.error(f"Error loading lead table: {e}")
        df = pd.DataFrame()

    if not df.empty:
        # Status filter
        if "STATUS" in df.columns:
            st_values = sorted(df["STATUS"].dropna().unique())
            st_filter = st.selectbox(
                "Filter by STATUS:",
                options=["All"] + list(st_values),
                index=0
            )
            if st_filter != "All":
                df = df[df["STATUS"] == st_filter]

        st.caption(f"Showing {len(df)} leads")
        st.dataframe(df, use_container_width=True)

        # Update status UI
        st.write("---")
        st.markdown("### ✏️ Update Lead Status")
        col1, col2 = st.columns(2)
        with col1:
            lead_id = st.text_input("LEAD_ID:")
        with col2:
            new_status = st.selectbox(
                "New Status:",
                options=["New", "In Follow-up", "Converted", "Not Interested", "Lost"]
            )
        if st.button("Update Lead"):
            if lead_id:
                try:
                    run_execute(
                        "UPDATE lead SET STATUS = %s WHERE LEAD_ID = %s;",
                        (new_status, lead_id)
                    )
                    st.success(f"Lead {lead_id} status updated to {new_status}.")
                    st.cache_data.clear()
                except Exception as e:
                    st.error(f"Error updating lead: {e}")
            else:
                st.warning("Please enter LEAD_ID.")

        # Status distribution chart
        st.write("---")
        st.markdown("#### 📊 Lead Status Distribution")
        try:
            rows = run_query("""
                SELECT STATUS, COUNT(*) AS count
                FROM lead
                GROUP BY STATUS;
            """)
            if rows:
                dfl = pd.DataFrame(rows).set_index("STATUS")
                st.bar_chart(dfl["count"])
            else:
                st.info("No lead status data.")
        except Exception as e:
            st.error(f"Error loading lead status chart: {e}")
    else:
        st.info("Lead table is empty or not accessible.")


# ================== 7. RESULTS ==================
elif page == "Results":
    st.subheader("📑 Result & Performance Analytics")

    # Try to show joined result with student + test + course
    df = pd.DataFrame()
    joined_ok = False

    try:
        rows = run_query("""
            SELECT 
                r.RESULT_ID,
                r.STUDENT_ID,
                s.NAME AS STUDENT_NAME,
                r.TEST_ID,
                t.TEST_NAME,
                t.COURSE_ID,
                c.COURSE_NAME,
                r.MARKS_OBTAINED,
                r.GRADE,
                r.REMARKS
            FROM result r
            JOIN student s ON r.STUDENT_ID = s.STUDENT_ID
            JOIN test t    ON r.TEST_ID = t.TEST_ID
            JOIN course c  ON t.COURSE_ID = c.COURSE_ID;
        """)
        df = pd.DataFrame(rows)
        joined_ok = True
    except Exception as e:
        st.warning(f"Joined result view not available, showing raw result table. Details: {e}")
        try:
            df = get_table_df("result")
        except Exception as e2:
            st.error(f"Error loading result table: {e2}")
            df = pd.DataFrame()

    if not df.empty:
        # Filters: course / student
        if "COURSE_NAME" in df.columns:
            courses = sorted(df["COURSE_NAME"].dropna().unique())
            c_filter = st.selectbox(
                "Filter by COURSE_NAME:",
                options=["All"] + list(courses),
                index=0
            )
            if c_filter != "All":
                df = df[df["COURSE_NAME"] == c_filter]

        if "STUDENT_ID" in df.columns:
            sids = sorted(df["STUDENT_ID"].dropna().unique())
            sid_filter = st.selectbox(
                "Filter by STUDENT_ID:",
                options=["All"] + list(sids),
                index=0
            )
            if sid_filter != "All":
                df = df[df["STUDENT_ID"] == sid_filter]

        st.caption(f"Showing {len(df)} result rows")
        st.dataframe(df, use_container_width=True)

        # Charts (if marks available)
        if "MARKS_OBTAINED" in df.columns:
            st.write("---")
            col_r1, col_r2 = st.columns(2)

            with col_r1:
                st.markdown("#### 📊 Average Marks by Course")
                if "COURSE_NAME" in df.columns:
                    try:
                        m1 = df.groupby("COURSE_NAME")["MARKS_OBTAINED"].mean()
                        st.bar_chart(m1)
                    except Exception as e:
                        st.error(f"Error plotting course-wise avg marks: {e}")
                else:
                    st.info("COURSE_NAME not available for chart.")

            with col_r2:
                st.markdown("#### 📊 Average Marks by Test")
                if "TEST_NAME" in df.columns:
                    try:
                        m2 = df.groupby("TEST_NAME")["MARKS_OBTAINED"].mean()
                        st.bar_chart(m2)
                    except Exception as e:
                        st.error(f"Error plotting test-wise avg marks: {e}")
                else:
                    st.info("TEST_NAME not available for chart.")
    else:
        st.info("Result data is empty or not accessible.")


# ================== 8. FACULTY & CLASSES ==================
elif page == "Faculty & Classes":
    st.subheader("🧑‍🏫 Faculty Workload & Class Schedule")

    # Faculty table
    try:
        df_fac = get_table_df("faculty")
        st.markdown("### Faculty List")
        st.dataframe(df_fac, use_container_width=True)
    except:
        st.info("Faculty table not found or empty.")

    st.write("---")
    st.markdown("### Class Schedule & Faculty Load")

    try:
        df_cs = get_table_df("class_schedule")
    except Exception as e:
        st.error(f"Error loading class_schedule: {e}")
        df_cs = pd.DataFrame()

    if not df_cs.empty:
        # Filter by FACULTY_ID
        if "FACULTY_ID" in df_cs.columns:
            fac_values = sorted(df_cs["FACULTY_ID"].dropna().unique())
            fac_choice = st.selectbox(
                "Filter by FACULTY_ID:",
                options=["All"] + list(fac_values),
                index=0
            )
            if fac_choice != "All":
                df_cs = df_cs[df_cs["FACULTY_ID"] == fac_choice]

        st.caption(f"Showing {len(df_cs)} class schedule rows")
        st.dataframe(df_cs, use_container_width=True)

        # Faculty load chart
        if "FACULTY_ID" in df_cs.columns:
            st.markdown("#### 📊 Faculty-wise Class Count")
            try:
                fload = df_cs.groupby("FACULTY_ID").size().reset_index(name="class_count")
                fload = fload.set_index("FACULTY_ID")
                st.bar_chart(fload["class_count"])
            except Exception as e:
                st.error(f"Error plotting faculty load: {e}")
    else:
        st.info("No class schedule data available.")


# ================== 9. ROOMS UTILIZATION ==================
elif page == "Rooms Utilization":
    st.subheader("🏫 Room / Class Utilization")

    try:
        df_cs = get_table_df("class_schedule")
    except Exception as e:
        st.error(f"Error loading class_schedule: {e}")
        df_cs = pd.DataFrame()

    try:
        df_room = get_table_df("room")
    except:
        df_room = pd.DataFrame()

    if not df_cs.empty:
        st.markdown("### Room-wise Schedule")

        if "ROOM_ID" in df_cs.columns:
            st.caption(f"Total scheduled classes: {len(df_cs)}")
            st.dataframe(df_cs, use_container_width=True)

            st.markdown("#### 📊 Room-wise Class Count")
            try:
                rload = df_cs.groupby("ROOM_ID").size().reset_index(name="class_count")
                rload = rload.set_index("ROOM_ID")
                st.bar_chart(rload["class_count"])
            except Exception as e:
                st.error(f"Error plotting room utilization: {e}")
        else:
            st.info("ROOM_ID column not found in class_schedule.")
    else:
        st.info("No class schedule data available for rooms.")

    if not df_room.empty:
        st.write("---")
        st.markdown("### Room Master Table")
        st.dataframe(df_room, use_container_width=True)


# ================== 10. ALL TABLES VIEWER (AUTO FROM DB) ==================
elif page == "All Tables":
    st.subheader("🗄️ All Tables Viewer (Auto-detected)")

    try:
        all_tables = get_all_tables()
    except Exception as e:
        st.error(f"Error fetching table list: {e}")
        all_tables = []

    if not all_tables:
        st.warning("No tables found or unable to read table list.")
    else:
        table_name = st.sidebar.selectbox("Select Table:", all_tables, index=0)
        st.markdown(f"### `{table_name}`")

        col1, col2 = st.columns([2, 1])
        with col1:
            search_text = st.text_input("Search (matches any column):", "")
        with col2:
            max_rows = st.number_input("Max rows to show:", min_value=10, max_value=2000, value=500, step=10)

        try:
            df = get_table_df(table_name)
            total_rows = len(df)
            st.caption(f"Total rows: {total_rows}")

            if search_text.strip():
                s = search_text.lower()
                df_filtered = df[df.apply(
                    lambda row: row.astype(str).str.lower().str.contains(s).any(),
                    axis=1
                )]
            else:
                df_filtered = df

            if df_filtered.empty:
                st.warning("No rows match your search.")
            else:
                df_show = df_filtered.head(int(max_rows))
                st.dataframe(df_show, use_container_width=True)

                csv = df_filtered.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="⬇️ Download filtered data as CSV",
                    data=csv,
                    file_name=f"{table_name}.csv",
                    mime="text/csv"
                )
        except Exception as e:
            st.error(f"Error loading table `{table_name}`: {e}")
            st.info("Check if table exists and names are correct.")
