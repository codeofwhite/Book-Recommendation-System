<template>
    <div class="about-us-container">
        <h1>关于我们的图书推荐系统</h1>

        <section class="mission-statement">
            <h2>我们的使命</h2>
            <p>
                欢迎来到我们的图书推荐系统！我们的使命是帮助读者找到他们的下一本挚爱书籍。在这个充满海量文学作品的世界里，找到完美读物既令人愉悦，有时也让人不知所措。我们利用先进的算法和对文学品味的深入理解，为您带来真正符合您偏好的个性化推荐。
            </p>
        </section>

        <section class="how-it-works">
            <h2>工作原理</h2>
            <p>
                我们的系统以您为中心设计。当您通过给书籍评分、标记已读或将其添加到愿望清单来与我们的平台互动时，我们智能的引擎会学习您的独特阅读习惯。我们分析各种因素，包括您的流派偏好、作者风格、出版日期，甚至评论中表达的情感，从而提供高度准确的推荐。您使用我们的系统越多，它就越能理解您的文学品味！
            </p>
            <ul>
                <li><strong>个性化推荐：</strong> 根据您的阅读历史和偏好。</li>
                <li><strong>多样化分类：</strong> 探索从小说、非小说到诗歌和科幻等各种流派。</li>
                <li><strong>社区互动：</strong> 发现其他读者喜欢什么，并分享您的见解。</li>
                <li><strong>易于使用的界面：</strong> 为每位爱书之人提供无缝直观的体验。</li>
            </ul>
        </section>

        <section class="our-team">
            <h2>我们的团队</h2>
            <p>
                我们是一支充满热情的开发人员、数据科学家和狂热读者组成的团队，我们深信书籍的力量。我们在机器学习、用户体验设计和文学方面的集体专业知识，促使我们致力于创建一个既智能又使用愉快的推荐系统。我们不断努力改进算法并扩展图书库，确保您总能找到新鲜有趣的东西。
            </p>
        </section>

        <section class="contact-us">
            <h2>联系我们</h2>
            <p>
                我们乐于倾听用户的声音！如果您有任何问题、反馈或建议，请随时与我们联系。您的宝贵意见有助于我们不断完善图书推荐系统。
            </p>
            <p>您可以通过以下方式联系我们：<a href="mailto:support@bookrecsys.com">support@bookrecsys.com</a></p>
        </section>

        <section class="acknowledgements">
            <h2>致谢</h2>
            <p>
                我们感谢开源社区和各种数据提供者，他们的资源对本平台的构建和增强至关重要。
            </p>
        </section>
    </div>
</template>

<script>
export default {
    name: 'AboutUs',
    // 对于简单的“关于我们”页面，通常主要包含静态内容，无需太多组件特定逻辑。
};
</script>

<style scoped>
.about-us-container {
    max-width: 900px;
    margin: 40px auto;
    padding: 30px;
    background-color: #f9f9f9;
    border-radius: 10px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    font-family: 'Arial', sans-serif;
    color: #333;
    line-height: 1.7;
}

h1 {
    text-align: center;
    color: #2c3e50;
    margin-bottom: 40px;
    font-size: 2.8em;
    font-weight: bold;
}

h2 {
    color: #34495e;
    margin-top: 30px;
    margin-bottom: 15px;
    font-size: 1.8em;
    border-bottom: 2px solid #eee;
    padding-bottom: 5px;
}

p {
    margin-bottom: 15px;
    font-size: 1.1em;
}

ul {
    list-style-type: disc;
    margin-left: 25px;
    margin-bottom: 15px;
}

ul li {
    margin-bottom: 8px;
    font-size: 1.1em;
}

a {
    color: #3498db;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

.mission-statement,
.how-it-works,
.our-team,
.contact-us,
.acknowledgements {
    margin-bottom: 30px;
    padding: 20px;
    background-color: #ffffff;
    border-left: 5px solid #3498db;
    border-radius: 5px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

.how-it-works ul {
    list-style-type: none;
    /* 移除默认的项目符号 */
    padding: 0;
}

.how-it-works ul li {
    position: relative;
    /* 用于自定义项目符号 */
    padding-left: 30px;
    /* 为自定义项目符号留出空间 */
    margin-bottom: 10px;
}

.how-it-works ul li::before {
    content: '📚';
    /* 自定义表情符号作为项目符号 */
    position: absolute;
    left: 0;
    top: 0;
    font-size: 1.2em;
}
</style>