from dotenv import load_dotenv, find_dotenv
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity


# 加载环境变量以获取API密钥
_ = load_dotenv(find_dotenv())
client = OpenAI()


def find_similar_records(document_path, query, similarity_threshold=0.8):
    """
    在主文档中查找与查询相似度高于阈值的所有记录。

    参数:
    - document_path: str, 主文档的文件路径。
    - query: str, 用户的查询问题。
    - similarity_threshold: float, 相似度阈值，返回高于该阈值的所有记录。

    返回:
    - list, 所有相似度超过阈值的记录（如果存在），否则返回空列表。
    """
    # 读取主文档内容
    with open(document_path, 'r', encoding='utf-8') as file:
        documents = eval(file.read())

    # 提取文档描述
    document_texts = [doc['record_descrpt'] for doc in documents]

    # 为每个段落生成嵌入向量
    document_embeddings = []
    for text in document_texts:
        response = client.embeddings.create(
            model="text-embedding-v3",
            input=text
        )
        embedding = response.data[0].embedding
        document_embeddings.append(embedding)

    # 为用户的问题生成嵌入向量
    query_response = client.embeddings.create(
        model="text-embedding-v3",
        input=query
    )
    query_embedding = query_response.data[0].embedding

    # 计算余弦相似度
    similarities = cosine_similarity([query_embedding], document_embeddings)[0]

    # 筛选出相似度超过阈值的记录
    similar_records = []
    for idx, score in enumerate(similarities):
        if score >= similarity_threshold:
            similar_records.append(documents[idx])

    # 返回所有相似度超过阈值的记录
    return similar_records


# 示例调用
document_path = '/Users/admin/Desktop/projects/qianwennotebook/git/ai_note_book/output.txt'
query = "东东"
similarity_threshold = 0.8  # 设定一个相似度阈值
results = find_similar_records(document_path, query, similarity_threshold)

if results:
    print("找到的所有相似记录:")
    print(results)
else:
    print("没有找到符合相似度阈值的记录。")
