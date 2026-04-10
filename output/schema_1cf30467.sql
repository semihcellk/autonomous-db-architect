CREATE TABLE Students (
    student_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    enrollment_date TEXT NOT NULL
);

CREATE TABLE Departments (
    department_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    location TEXT
);

CREATE TABLE Professors (
    professor_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    department_id INTEGER,
    FOREIGN KEY (department_id) REFERENCES Departments(department_id)
);

CREATE TABLE Courses (
    course_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    credits INTEGER NOT NULL,
    department_id INTEGER,
    professor_id INTEGER,
    FOREIGN KEY (department_id) REFERENCES Departments(department_id),
    FOREIGN KEY (professor_id) REFERENCES Professors(professor_id)
);

CREATE TABLE Enrollments (
    student_id INTEGER,
    course_id INTEGER,
    grade INTEGER,
    PRIMARY KEY (student_id, course_id),
    CHECK (grade BETWEEN 0 AND 100),
    FOREIGN KEY (student_id) REFERENCES Students(student_id),
    FOREIGN KEY (course_id) REFERENCES Courses(course_id)
);