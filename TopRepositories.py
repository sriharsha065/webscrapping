#!/usr/bin/env python
# coding: utf-8

# # web-scrapping
# 
# Use the "Run" button to execute the code.

# ### Project Outline
# We're going to scrape https://github.com/topics
# We'll get a list of topics. For each topic, we'll get topic title, topic page URL and topic description
# For each topic, we'll get the top 25 repositories in the topic from the topic page
# For each repository, we'll grab the repo name, username, stars and repo URL
# For each topic we'll create a CSV file in the following format:
# Repo Name,Username,Stars,Repo URL
# three.js,mrdoob,69700,https://github.com/mrdoob/three.js
# libgdx,libgdx,18300,https://github.com/libgdx/libgdx

# In[10]:


get_ipython().system('pip install requests --upgrade --quiet')


# In[2]:


import requests


# In[3]:


topics_url = 'https://github.com/topics'


# In[4]:


response = requests.get(topics_url)


# In[5]:


response.status_code


# In[6]:


len(response.text)


# In[7]:


page_contents = response.text


# In[8]:


page_contents[:1000]


# In[9]:


with open('webpage.html', 'w') as f:
    f.write(page_contents)


# ### Use Beautiful Soup to parse and extract information

# In[11]:


get_ipython().system('pip install beautifulsoup4 --upgrade --quiet')


# In[12]:


from bs4 import BeautifulSoup


# In[13]:


doc = BeautifulSoup(page_contents, 'html.parser')


# In[25]:


selection_class='f3 lh-condensed mb-0 mt-1 Link--primary'
topic_title_tags=doc.find_all('p',{'class':selection_class})


# In[26]:


len(topic_title_tags)


# In[28]:


topic_title_tags[:5]


# In[38]:


desc_selector="f5 color-fg-muted mb-0 mt-1"
topic_desc_tags=doc.find_all('p',{'class':desc_selector})


# In[30]:


topic_desc_tags[:5]


# In[40]:


topic_title_tag0 = topic_title_tags[0]


# In[32]:


div_tag = topic_title_tag0.parent


# In[35]:


topic_link_tags = doc.find_all('a', {'class': 'no-underline flex-1 d-flex flex-column'})


# In[36]:


len(topic_link_tags)


# In[41]:


topic0_url = "https://github.com" + topic_link_tags[0]['href']
print(topic0_url)


# In[63]:


topic_titles=[]
topic_descs=[]
topic_urls=[]
base_url='https://github.com'
for tag in topic_title_tags:
    topic_titles.append(tag.text)
for tag in topic_desc_tags:
    topic_descs.append(tag.text.strip())
for url in topic_link_tags:
    topic_urls.append(base_url+url['href'])


# In[64]:


topic_titles
topic_descs
topic_urls


# In[52]:


get_ipython().system('pip install pandas --quiet')


# In[57]:


import pandas as pd


# In[65]:


topics_dict={'title':topic_titles,
            'description':topic_descs,
             'url':topic_urls
            }
topics_df=pd.DataFrame(topics_dict)


# In[66]:


topics_df


# ### Create CSV file(s) with the extracted information

# In[68]:


topics_df.to_csv('topics.csv',index=None)


# ### Getting information out of a topic page

# In[69]:


topic_page_url=topic_urls[0]


# In[70]:


topic_page_url


# In[71]:


response=requests.get(topic_page_url)


# In[72]:


response.status_code


# In[74]:


len(response.text)


# In[88]:


topic_doc=BeautifulSoup(response.text,'html.parser')


# In[106]:


h3_selection_class = 'f3 color-fg-muted text-normal lh-condensed'
repo_tags = topic_doc.find_all('h3', {'class': h3_selection_class} )


# In[107]:


repo_tags


# In[114]:


a_tags=repo_tags[0].find_all('a')


# In[115]:


a_tags[0].text.strip()


# In[116]:


a_tags[1].text.strip()


# In[117]:


a_tags[1]['href']


# In[118]:


base_url


# In[119]:


repo_url=base_url+a_tags[1]['href']


# In[120]:


repo_url


# In[121]:


print(repo_url)


# In[124]:


star_tags=topic_doc.find_all('span',{'class':'Counter js-social-count'})


# In[125]:


star_tags[0]


# In[126]:


star_tags[0].text.strip()


# In[131]:


def parse_star_count(stars_str):
    stars_str=stars_str.strip()
    if stars_str[-1]=='k':
        return int(float(stars_str[:-1])*1000)
    return int(stars_str)


# In[132]:


parse_star_count(star_tags[0].text.strip())


# In[133]:


def get_repo_info(h3_tag,star_tag):
    a_tags=h3_tag.find_all('a')
    username=a_tags[0].text.strip()
    repo_name = a_tags[1].text.strip()
    repo_url =  base_url + a_tags[1]['href']
    stars = parse_star_count(star_tag.text.strip())
    return username, repo_name, stars, repo_url


# In[135]:


get_repo_info(repo_tags[0],star_tags[0])


# In[136]:


topic_repos_dict = {
    'username': [],
    'repo_name': [],
    'stars': [],
    'repo_url': []
}


for i in range(len(repo_tags)):
    repo_info = get_repo_info(repo_tags[i], star_tags[i])
    topic_repos_dict['username'].append(repo_info[0])
    topic_repos_dict['repo_name'].append(repo_info[1])
    topic_repos_dict['stars'].append(repo_info[2])
    topic_repos_dict['repo_url'].append(repo_info[3])


# In[137]:


topic_repos_dict


# In[138]:


topic_repos_df=pd.DataFrame(topic_repos_dict)


# In[139]:


topic_repos_df


# In[168]:


import os

def get_topic_page(topic_url):
    # Download the page
    response = requests.get(topic_url)
    # Check successful response
    if response.status_code != 200:
        raise Exception('Failed to load page {}'.format(topic_url))
    # Parse using Beautiful soup
    topic_doc = BeautifulSoup(response.text, 'html.parser')
    return topic_doc

def get_repo_info(h1_tag, star_tag):
    # returns all the required info about a repository
    a_tags = h1_tag.find_all('a')
    username = a_tags[0].text.strip()
    repo_name = a_tags[1].text.strip()
    repo_url =  base_url + a_tags[1]['href']
    stars = parse_star_count(star_tag.text.strip())
    return username, repo_name, stars, repo_url

def get_topic_repos(topic_doc):
    # Get the h1 tags containing repo title, repo URL and username
    h1_selection_class = 'f3 color-fg-muted text-normal lh-condensed'
    repo_tags = topic_doc.find_all('h3', {'class': h1_selection_class} )
    # Get star tags
    star_tags = topic_doc.find_all('span', { 'class': 'Counter js-social-count'})
    
    topic_repos_dict = { 'username': [], 'repo_name': [], 'stars': [],'repo_url': []}

    # Get repo info
    for i in range(len(repo_tags)):
        repo_info = get_repo_info(repo_tags[i], star_tags[i])
        topic_repos_dict['username'].append(repo_info[0])
        topic_repos_dict['repo_name'].append(repo_info[1])
        topic_repos_dict['stars'].append(repo_info[2])
        topic_repos_dict['repo_url'].append(repo_info[3])
        
    return pd.DataFrame(topic_repos_dict)


# In[169]:


url5=topic_urls[5]


# In[170]:


topic5_doc=get_topic_page(url5)


# In[171]:


topic5_repos=get_topic_repos(topic5_doc)
topic5_repos


# In[172]:


topic5_repos.to_csv('ansible.csv',index=None)


# In[173]:


import jovian


# In[ ]:





# In[174]:


jovian.commit()


# In[ ]:




