# import hashlib
# from pybloom_live import BloomFilter
# import sqlite3
# import os
# import pandas as pd
# import streamlit as st

# # Define the Flajolet-Martin class for estimating unique queries
# class FlajoletMartin:
#     def __init__(self, num_hashes):
#         self.num_hashes = num_hashes
#         self.max_zeros = [0] * num_hashes

#     def _hash(self, query, i):
#         # Create different hash functions by appending i to the query
#         hash_value = hashlib.md5((query + str(i)).encode()).hexdigest()
#         bin_hash = bin(int(hash_value, 16))[2:]
#         return bin_hash

#     def add_query(self, query):
#         for i in range(self.num_hashes):
#             bin_hash = self._hash(query, i)
#             # Count trailing zeros in the binary hash
#             trailing_zeros = len(bin_hash) - len(bin_hash.rstrip('0'))
#             self.max_zeros[i] = max(self.max_zeros[i], trailing_zeros)

#     def estimate_unique_queries(self):
#         # Estimate the number of unique queries as 2^average_max_zeros
#         avg_max_zeros = sum(self.max_zeros) / len(self.max_zeros)
#         return 2 ** avg_max_zeros


# # Function to run the search engine query analytics with dynamic data
# def search_engine_query_analytics(df):
#     bloom_filter = BloomFilter(capacity=1000, error_rate=0.001)  # Initialize Bloom Filter
#     fm_algorithm = FlajoletMartin(num_hashes=10)  # Initialize Flajolet-Martin algorithm

#     # Extract queries from the DataFrame (use 'Title' or 'URL' depending on your needs)
#     queries = df['Title'].dropna().tolist()  # Drop any rows with missing values and convert to list

#     print("Starting Search Engine Query Analytics...\n")

#     for query in queries:
#         if query in bloom_filter:
#             print(f"Duplicate query detected: '{query}'")
#         else:
#             print(f"New query added: '{query}'")
#             bloom_filter.add(query)
#             fm_algorithm.add_query(query)

#     estimated_unique_queries = fm_algorithm.estimate_unique_queries()
#     print(f"\nEstimated number of unique queries: {int(estimated_unique_queries)}")


# # Function to fetch Chrome history data and run the analytics
# def get_chrome_history_and_run_analytics():
#     # Get the username of the currently logged-in user
#     username = os.getlogin()

#     # Path to the Chrome history database file
#     history_db_path = f"C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History"

#     # Check if the history file exists
#     if not os.path.exists(history_db_path):
#         print(f"History file not found at {history_db_path}. Make sure the path is correct and Chrome is closed.")
#         return

#     # Connect to the SQLite database
#     conn = sqlite3.connect(history_db_path)
#     cursor = conn.cursor()

#     # Define the query to get URLs and titles from the history database
#     query = """
#     SELECT urls.url, urls.title, visits.visit_time
#     FROM urls, visits
#     WHERE urls.id = visits.url
#     ORDER BY visits.visit_time DESC
#     LIMIT 100  -- Adjust the limit as needed
#     """

#     # Execute the query and fetch results
#     cursor.execute(query)
#     results = cursor.fetchall()

#     # Close the connection to the database
#     conn.close()

#     # Convert results to a pandas DataFrame
#     df = pd.DataFrame(results, columns=["URL", "Title", "Visit Time"])

#     # for streamlit
#     return df

#     # Run the search engine query analytics with the DataFrame data
#     # search_engine_query_analytics(df) for console


# def main():
#     st.title("Chrome History Query Analysis")

#     # Get Chrome history data
#     queries = get_chrome_history_and_run_analytics()

#     # Run the query analytics
#     duplicates, new_queries, estimated_unique_queries = search_engine_query_analytics(queries)

#     # Display the results in Streamlit
#     st.subheader("Results")
#     st.write(f"Number of new queries: {len(new_queries)}")
#     st.write(f"Estimated number of unique queries: {estimated_unique_queries}")
    
#     if duplicates:
#         st.write(f"Number of duplicate queries: {len(duplicates)}")
#         st.write("Duplicate Queries:")
#         st.dataframe(pd.DataFrame(duplicates, columns=["Duplicate Queries"]))
#     else:
#         st.write("No duplicate queries detected.")

# # Run the process
# if __name__ == "__main__":
#     get_chrome_history_and_run_analytics()


import hashlib
from pybloom_live import BloomFilter
import sqlite3
import os
import pandas as pd
import streamlit as st

# Define the Flajolet-Martin class for estimating unique queries
class FlajoletMartin:
    def __init__(self, num_hashes):
        self.num_hashes = num_hashes
        self.max_zeros = [0] * num_hashes

    def _hash(self, query, i):
        hash_value = hashlib.md5((query + str(i)).encode()).hexdigest()
        bin_hash = bin(int(hash_value, 16))[2:]
        return bin_hash

    def add_query(self, query):
        for i in range(self.num_hashes):
            bin_hash = self._hash(query, i)
            trailing_zeros = len(bin_hash) - len(bin_hash.rstrip('0'))
            self.max_zeros[i] = max(self.max_zeros[i], trailing_zeros)

    def estimate_unique_queries(self):
        avg_max_zeros = sum(self.max_zeros) / len(self.max_zeros)
        return 2 ** avg_max_zeros


# Function to run the search engine query analytics with dynamic data
def search_engine_query_analytics(df):
    bloom_filter = BloomFilter(capacity=1000, error_rate=0.001)
    fm_algorithm = FlajoletMartin(num_hashes=10)

    queries = df['Title'].dropna().tolist()
    duplicates = []
    new_queries = []

    for query in queries:
        if query in bloom_filter:
            duplicates.append(query)
        else:
            new_queries.append(query)
            bloom_filter.add(query)
            fm_algorithm.add_query(query)

    estimated_unique_queries = fm_algorithm.estimate_unique_queries()
    return duplicates, new_queries, int(estimated_unique_queries)


# Function to fetch Chrome history data and run the analytics
def get_chrome_history_and_run_analytics():
    username = os.getlogin()
    history_db_path = f"C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History"

    if not os.path.exists(history_db_path):
        st.error(f"History file not found at {history_db_path}. Make sure the path is correct and Chrome is closed.")
        return pd.DataFrame()

    conn = sqlite3.connect(history_db_path)
    cursor = conn.cursor()

    query = """
    SELECT urls.url, urls.title, visits.visit_time
    FROM urls, visits
    WHERE urls.id = visits.url
    ORDER BY visits.visit_time DESC
    LIMIT 100
    """

    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

    df = pd.DataFrame(results, columns=["URL", "Title", "Visit Time"])
    return df


def main():
    st.title("Search Engine Query Analysis")

    # Get Chrome history data
    df = get_chrome_history_and_run_analytics()
    
    if not df.empty:
        # Run the query analytics
        duplicates, new_queries, estimated_unique_queries = search_engine_query_analytics(df)

        # Display the results in Streamlit
        st.subheader("Results")
        st.write(f"Number of new queries: {len(new_queries)}")
        st.write(f"Estimated number of unique queries: {estimated_unique_queries}")

        if duplicates:
            st.write(f"Number of duplicate queries: {len(duplicates)}")
            st.write("Unique Queries:")
            st.dataframe(pd.DataFrame(new_queries, columns=["Unique Queries"]), use_container_width=True)
            st.write("Duplicate Queries:")
            st.dataframe(pd.DataFrame(duplicates, columns=["Duplicate Queries"]), use_container_width=True)
        else:
            st.write("No duplicate queries detected.")

# Run the process
if __name__ == "__main__":
    main()  # Call the main function
