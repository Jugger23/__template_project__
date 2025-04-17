-- Supermarkt-Angebot
CREATE TABLE offers (
  id SERIAL PRIMARY KEY,
  supermarket VARCHAR,
  product_id VARCHAR,
  name VARCHAR,
  brand VARCHAR,
  price DECIMAL,
  discount DECIMAL,
  quantity VARCHAR,
  scraped_at TIMESTAMP
);

-- Zutat
CREATE TABLE ingredients (
  id SERIAL PRIMARY KEY,
  name VARCHAR,
  default_brand VARCHAR
);

-- Gericht
CREATE TABLE recipes (
  id SERIAL PRIMARY KEY,
  title VARCHAR,
  description TEXT
);

-- Rezept-Zutaten-Verknüpfung
CREATE TABLE recipe_ingredients (
  recipe_id INTEGER REFERENCES recipes(id),
  ingredient_id INTEGER REFERENCES ingredients(id),
  amount VARCHAR,
  unit VARCHAR,
  PRIMARY KEY(recipe_id, ingredient_id)
);

-- Haushaltsbestand
CREATE TABLE pantry (
  user_id INTEGER,
  ingredient_id INTEGER REFERENCES ingredients(id),
  amount VARCHAR,
  unit VARCHAR,
  PRIMARY KEY(user_id, ingredient_id)
);