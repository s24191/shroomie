-- Create table for Region
CREATE TABLE Region (
    id INTEGER PRIMARY KEY,
    nam TEXT NOT NULL
);

-- Create table for Edible
CREATE TABLE Edible (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

-- Create table for Mushroom
CREATE TABLE Mushroom (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    desc TEXT,
    image BLOB,
    edible_id INTEGER,
    FOREIGN KEY (edible_id) REFERENCES Edible(id)
);

-- Create table for User
CREATE TABLE User (
    id INTEGER PRIMARY KEY,
    login TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT,
    phone_number INTEGER,
    date_of_birth DATE
);

-- Create table for Mushroom_Region to establish a many-to-many relationship between Mushroom and Region
CREATE TABLE Mushroom_Region (
    Region_id INTEGER,
    Mushroom_id INTEGER,
    PRIMARY KEY (Region_id, Mushroom_id),
    FOREIGN KEY (Region_id) REFERENCES Region(id),
    FOREIGN KEY (Mushroom_id) REFERENCES Mushroom(id)
);

-- Create table for History
CREATE TABLE History (
    id INTEGER PRIMARY KEY,
    User_id INTEGER,
    Mushroom_id INTEGER,
    user_image INTEGER,
    date DATE,
    FOREIGN KEY (User_id) REFERENCES User(id),
    FOREIGN KEY (Mushroom_id) REFERENCES Mushroom(id)
);
-- Insert into Region
INSERT INTO Region (id, nam) VALUES (1, 'North America');

-- Insert into Edible
INSERT INTO Edible (id, name) VALUES (1, 'Yes');

-- Insert into Mushroom
INSERT INTO Mushroom (id, name, desc, image, edible_id) VALUES (1, 'Agaricus', 'Commonly known as button mushroom', NULL, 1);
INSERT INTO Mushroom (id, name, desc, image, edible_id) VALUES (2, 'Amanita', 'Known for some toxic varieties', NULL, 1);
INSERT INTO Mushroom (id, name, desc, image, edible_id) VALUES (3, 'Boletus', 'Large mushrooms often with pores under the cap', NULL, 1);
INSERT INTO Mushroom (id, name, desc, image, edible_id) VALUES (4, 'Cortinarius', 'Often has a web-like veil', NULL, 1);
INSERT INTO Mushroom (id, name, desc, image, edible_id) VALUES (5, 'Entoloma', 'Brightly colored, some are toxic', NULL, 1);
INSERT INTO Mushroom (id, name, desc, image, edible_id) VALUES (6, 'Hygrocybe', 'Known for bright colors and waxy cap', NULL, 1);
INSERT INTO Mushroom (id, name, desc, image, edible_id) VALUES (7, 'Lactarius', 'Produces a milky fluid', NULL, 1);
INSERT INTO Mushroom (id, name, desc, image, edible_id) VALUES (8, 'Russula', 'Brittle mushrooms with diverse colors', NULL, 1);
INSERT INTO Mushroom (id, name, desc, image, edible_id) VALUES (9, 'Suillus', 'Often associated with pine trees', NULL, 1);

-- Insert into User
INSERT INTO User (id, login, password, email, phone_number, date_of_birth) 
VALUES (1, 'mushroom_lover', 'password123', 'mushroom_lover@example.com', 1234567890, '1990-01-01');

-- Insert into Mushroom_Region
INSERT INTO Mushroom_Region (Region_id, Mushroom_id) VALUES (1, 1);
INSERT INTO Mushroom_Region (Region_id, Mushroom_id) VALUES (1, 2);
INSERT INTO Mushroom_Region (Region_id, Mushroom_id) VALUES (1, 3);
INSERT INTO Mushroom_Region (Region_id, Mushroom_id) VALUES (1, 4);
INSERT INTO Mushroom_Region (Region_id, Mushroom_id) VALUES (1, 5);
INSERT INTO Mushroom_Region (Region_id, Mushroom_id) VALUES (1, 6);
INSERT INTO Mushroom_Region (Region_id, Mushroom_id) VALUES (1, 7);
INSERT INTO Mushroom_Region (Region_id, Mushroom_id) VALUES (1, 8);
INSERT INTO Mushroom_Region (Region_id, Mushroom_id) VALUES (1, 9);

-- Insert into History
INSERT INTO History (id, User_id, Mushroom_id, user_image, date) 
VALUES (1, 1, 1, NULL, '2024-11-06');
