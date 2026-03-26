import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout='wide')

df = pd.read_csv('india_cleaned.csv')
numeric_columns = ['Latitude', 'Longitude', 'Population', 'Households_with_Internet', 'sex ratio', 'literacy rate']
df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
state_list = list(df['State'].unique())
state_list.insert(0,'Overall India')

st.sidebar.title("India Data Analysis")
select_option = st.sidebar.selectbox('Select Type',state_list)
plot = st.sidebar.button('Plot Graph')

def overall():
    st.subheader("Summary")
    avg_literacy = df['literacy rate'].mean()
    min_literacy = df['literacy rate'].min()
    max_literacy = df['literacy rate'].max()

    col1, col2, col3 = st.columns(3)
    col1.metric("Overall India Avg Literacy", f"{avg_literacy:.2f}%")
    col2.metric("Minimum District Literacy", f"{min_literacy:.0f}%")
    col3.metric("Maximum District Literacy", f"{max_literacy:.0f}%")

    st.subheader("District-wise Literacy Rate and Population Map")
    fig = px.scatter_map(
        df,
        lat="Latitude",
        lon="Longitude",
        size="Population",
        hover_name="District",
        color='literacy rate',
        color_continuous_scale='Plasma',
        height=600,
        width=800,
        zoom=4
    )
    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig,width='stretch')

    st.subheader("Top States in Population")
    top_pop = df.groupby('State')['Population'].sum().sort_values(ascending=False).head(10)
    fig = px.bar(top_pop,x=top_pop.index,y=top_pop.values,
                 color=top_pop.index,labels={"x":"State","y":"Population"})
    st.plotly_chart(fig)

    col1,col2 = st.columns(2)

    with col1:
        st.subheader("Top states with high literacy rate")
        top_lit = df.groupby('State')['literacy rate'].mean().sort_values(ascending=False).head(5)
        fig = px.bar(top_lit, x=top_lit.values, y=top_lit.index, log_x=True, color=top_lit.index)
        st.plotly_chart(fig)

    with col2:
        st.subheader("Top states with internet Using")
        top_internet = df.groupby('State')['Households_with_Internet'].mean().sort_values(ascending=False).head(5)
        fig = px.bar(
            top_internet,
            x=top_internet.values,
            y=top_internet.index,
            color=top_internet.index,
            labels={"x": "Households with Internet", "y": "State"}
        )
        st.plotly_chart(fig)

def state_analysis(state):
    state_df = df[df['State'] == state].copy()
    state_df['Internet_per_1000'] = (state_df['Households_with_Internet'] / state_df['Population']) * 1000

    highest_literacy = state_df.loc[state_df['literacy rate'].idxmax()]
    highest_internet = state_df.loc[state_df['Households_with_Internet'].idxmax()]
    best_connected = state_df.loc[state_df['Internet_per_1000'].idxmax()]

    st.subheader(f"{state} Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Districts Covered", f"{state_df['District'].nunique()}")
    col2.metric("Total Population", f"{state_df['Population'].sum():,}")
    col3.metric("Average Literacy Rate", f"{state_df['literacy rate'].mean():.2f}%")
    col4.metric("Households with Internet", f"{state_df['Households_with_Internet'].sum():,}")

    st.markdown(
        f"""
        **Highlights**
        - Highest literacy district: **{highest_literacy['District']}** ({highest_literacy['literacy rate']:.0f}%)
        - Highest internet usage district: **{highest_internet['District']}** ({highest_internet['Households_with_Internet']:,} households)
        - Best internet reach per 1000 people: **{best_connected['District']}** ({best_connected['Internet_per_1000']:.2f})
        """
    )

    st.subheader(f"{state} District-wise Literacy Rate and Population Map")
    fig = px.scatter_map(
        state_df,
        lat="Latitude",
        lon="Longitude",
        size="Population",
        hover_name="District",
        color='literacy rate',
        color_continuous_scale='Plasma',
        height=550,
        zoom=5
    )
    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, width='stretch')

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Top districts by literacy rate")
        top_district_lit = state_df.nlargest(5, 'literacy rate')
        fig = px.bar(
            top_district_lit,
            x='literacy rate',
            y='District',
            color='District',
            orientation='h',
            labels={"literacy rate": "Literacy Rate (%)", "District": "District"}
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, width='stretch')

    with col2:
        st.subheader("Top districts by internet usage")
        top_district_internet = state_df.nlargest(5, 'Households_with_Internet')
        fig = px.bar(
            top_district_internet,
            x='Households_with_Internet',
            y='District',
            color='District',
            orientation='h',
            labels={"Households_with_Internet": "Households with Internet", "District": "District"}
        )
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, width='stretch')

    st.subheader("Literacy Rate vs Internet Usage")
    fig = px.scatter(
        state_df,
        x='literacy rate',
        y='Households_with_Internet',
        size='Population',
        color='Internet_per_1000',
        hover_name='District',
        color_continuous_scale='Viridis',
        labels={
            "literacy rate": "Literacy Rate (%)",
            "Households_with_Internet": "Households with Internet",
            "Internet_per_1000": "Internet per 1000"
        }
    )
    st.plotly_chart(fig, width='stretch')

    st.subheader("District-level Data")
    district_summary = state_df[
        ['District', 'Population', 'literacy rate', 'Households_with_Internet', 'Internet_per_1000']
    ].sort_values(['literacy rate', 'Households_with_Internet'], ascending=False)
    district_summary['Internet_per_1000'] = district_summary['Internet_per_1000'].round(2)
    st.dataframe(district_summary, width='stretch')


if plot:
    if select_option == 'Overall India':
        overall()
    else:
        state_analysis(select_option)


