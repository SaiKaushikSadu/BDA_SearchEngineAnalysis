import hashlib
from pybloom_live import BloomFilter
import sqlite3
import os
import shutil
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

# Function to create a copy of the Chrome history database
def create_database_copy():
    username = os.getlogin()
    source_path = f"C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History"
    destination_path = f"C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\History_copy"

    # Remove the existing copy if it exists
    if os.path.exists(destination_path):
        os.remove(destination_path)

    # Copy the original database to the new file
    shutil.copy(source_path, destination_path)

    return destination_path

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
    # Create a copy of the Chrome history database
    db_path = create_database_copy()

    if not os.path.exists(db_path):
        st.error(f"History file not found at {db_path}. Make sure the path is correct and Chrome is closed.")
        return pd.DataFrame()

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = """
    SELECT urls.url, urls.title, visits.visit_time
    FROM urls, visits
    WHERE urls.id = visits.url
    ORDER BY visits.visit_time DESC
    LIMIT 500
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
        # st.write(f"Number of new queries: {len(new_queries)}")
        st.write(f"Number of duplicate queries: {len(duplicates)}")
        st.write(f"Estimated number of unique queries: {estimated_unique_queries}")

        if duplicates:
            # Truncate site names to a maximum of 10 characters followed by '...' if necessary
            df['Short Title'] = df['Title'].apply(lambda x: x[:10] + '...' if len(x) > 10 else x)

            # Count duplicates for the bar chart
            duplicate_counts = pd.Series(duplicates).value_counts()
            duplicate_counts = duplicate_counts.reset_index()
            duplicate_counts.columns = ['Site', 'Count']
            duplicate_counts['Site'] = duplicate_counts['Site'].apply(lambda x: x[:10] + '...' if len(x) > 10 else x)

            # Plot bar chart
            st.subheader("Duplicate Queries Analysis")
            st.bar_chart(data=duplicate_counts.set_index('Site'), width=800)

            st.write(f"Number of duplicate queries: {len(duplicates)}")
            st.write("Unique Queries:")
            st.dataframe(pd.DataFrame(new_queries, columns=["Unique Queries"]), use_container_width=True)
            st.write("Duplicate Queries:")
            st.dataframe(pd.DataFrame(duplicates, columns=["Duplicate Queries"]), use_container_width=True)
        else:
            st.write("No duplicate queries detected.")

# Run the process
if __name__ == "__main__":
    main()
