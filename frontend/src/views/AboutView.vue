<!-- 关于页面 -->
<template>
    <div class="establishment-container">
        <h1 class="main-heading">关于书斋：我们的初衷</h1>

        <section class="chapter-section mission-statement">
            <h2 class="chapter-title">我们的使命</h2>
            <p class="chapter-paragraph">
                欢迎来到书斋——这里是你探索海量书籍的贴心向导。我们的目标很简单：帮每一位爱读书的人，找到下一本喜欢的书。
                如今好书太多，想挑到合心意的难免让人纠结。我们用先进的算法，结合对阅读喜好的精准把握，为你推荐专属的优质书籍。
            </p>
        </section>

        <section class="chapter-section how-it-works">
            <h2 class="chapter-title">我们的运作方式</h2>
            <p class="chapter-paragraph">
                我们的系统核心，就是围绕你的阅读经历打造。当你在平台上给书籍评分、标记已读或加入想读清单时，系统会悄悄记录你的阅读偏好。
                我们会分析你喜欢的 genres、作者风格、出版年代，甚至书评里的真实感受，让推荐更精准。你和平台互动越多，我们就越懂你的阅读口味！
            </p>
            <ul class="feature-list">
                <li>
                    <span class="feature-icon">★</span>
                    <strong>专属推荐：</strong> 根据你的阅读记录和喜好，量身打造推荐列表。
                </li>
                <li>
                    <span class="feature-icon">◆</span>
                    <strong>书籍种类丰富：</strong> 涵盖小说、非虚构、诗歌、科幻等各种类型，满足不同需求。
                </li>
                <li>
                    <span class="feature-icon">ↈ</span>
                    <strong>读者社区：</strong> 了解其他读者的喜好，也分享自己的阅读心得。
                </li>
                <li>
                    <span class="feature-icon">◊</span>
                    <strong>操作简单：</strong> 界面直观好上手，让每一位读者都能轻松使用。
                </li>
            </ul>
        </section>

        <section class="chapter-section our-team">
            <h2 class="chapter-title">我们的团队</h2>
            <p class="chapter-paragraph">
                我们是一群热爱开发的工程师、懂数据的专家，同时也是忠实的读者。我们相信文字的力量，
                结合机器学习、用户体验设计和文学领域的知识，打造出既智能又好用的书籍推荐系统。
                我们会不断优化算法、扩充书籍库，让你总能发现新鲜有趣的好书。
            </p>
        </section>

        <section class="chapter-section contact-us">
            <h2 class="chapter-title">联系我们</h2>
            <p class="chapter-paragraph">
                我们非常愿意倾听你的声音！如果你有任何问题、建议或想法，都可以随时联系我们。
                你的反馈对我们很重要，能帮助书斋变得更好。
            </p>
            <p class="chapter-paragraph contact-email">
                邮箱联系：
                <a href="mailto:curator@thescriptorium.com">curator@thescriptorium.com</a>
            </p>
        </section>

        <section class="chapter-section acknowledgements">
            <h2 class="chapter-title">致谢</h2>
            <p class="chapter-paragraph">
                特别感谢开源社区和各类数据提供商，他们的宝贵资源为这个平台的搭建和持续优化提供了重要支持。
            </p>
        </section>
    </div>
</template>

<script>
export default {
    name: 'AboutUs',
    // A simple "About Us" page primarily contains static content,
    // thus requiring minimal component-specific logic.
};
</script>

<style scoped>
/* --- General Container Styles --- */
.establishment-container {
    max-width: 1000px;
    /* Slightly wider for a more grand feel */
    margin: 50px auto;
    /* More vertical margin */
    padding: 40px;
    /* More internal padding */
    background-color: #fffaf0;
    /* Soft parchment white, consistent */
    border-radius: 12px;
    /* Gentler rounded corners */
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
    /* More refined shadow */
    font-family: 'Palatino Linotype', 'Book Antiqua', Palatino, serif;
    /* Classical font */
    color: #4e342e;
    /* Deep coffee brown text */
    line-height: 1.8;
    /* Increased line height for readability, like a printed book */
    border: 1px solid #d4b896;
    /* Subtle, complementary border */
}

/* --- Main Heading --- */
.main-heading {
    text-align: center;
    color: #5d4037;
    /* Darker brown for main title */
    margin-bottom: 50px;
    /* More space below main title */
    font-size: 3.5em;
    /* Grand and imposing */
    font-weight: 700;
    letter-spacing: 1px;
    /* Slight letter spacing */
    text-shadow: 2px 2px 5px rgba(0, 0, 0, 0.05);
    /* Subtle shadow */
}

/* --- Section Styling (Chapters) --- */
.chapter-section {
    margin-bottom: 40px;
    /* More space between sections */
    padding: 30px;
    /* More padding within each section */
    background-color: #ffffff;
    /* Clean white background for inner sections */
    border-left: 6px solid #8d6e63;
    /* Thicker, distinguished left border */
    border-radius: 8px;
    /* Slightly smaller border-radius for sections */
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.06);
    /* Softer shadow */
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    /* Hover effects */
}

.chapter-section:hover {
    transform: translateY(-5px);
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

/* --- Chapter Titles --- */
.chapter-title {
    color: #6d4c41;
    /* Softer brown for chapter titles */
    margin-top: 0;
    margin-bottom: 20px;
    /* More space below chapter title */
    font-size: 2.2em;
    /* Prominent chapter title */
    font-weight: 600;
    border-bottom: 1px dashed #d7ccc8;
    /* Dashed separator for elegance */
    padding-bottom: 10px;
    position: relative;
    text-align: left;
    /* Align titles to the left */
}

.chapter-title::before {
    content: '📜';
    /* Scroll icon for a classical touch */
    position: absolute;
    left: -40px;
    /* Position to the left of the border */
    top: 50%;
    transform: translateY(-50%);
    font-size: 0.8em;
    color: #bcaaa4;
    /* Muted color for the icon */
}

/* --- Paragraphs --- */
.chapter-paragraph {
    margin-bottom: 18px;
    /* Consistent paragraph spacing */
    font-size: 1.05em;
    /* Slightly larger text for readability */
    text-align: justify;
    /* Justify text for a formal, book-like appearance */
}

/* --- List Styling for "How It Works" --- */
.feature-list {
    list-style-type: none;
    /* Remove default bullet points */
    padding: 0;
    margin-left: 0;
    /* Align with paragraph text */
    margin-top: 25px;
    /* Space above list */
}

.feature-list li {
    position: relative;
    padding-left: 35px;
    /* Space for custom icon */
    margin-bottom: 12px;
    font-size: 1.05em;
    color: #5d4037;
    /* Darker brown for list items */
    text-align: left;
    /* Ensure list items align left */
}

.feature-list li strong {
    color: #4e342e;
    /* Stronger color for bolded text */
}

.feature-list li .feature-icon {
    position: absolute;
    left: 0;
    top: 0;
    font-size: 1.4em;
    /* Larger icon */
    color: #a1887f;
    /* Muted color for icons */
    font-weight: bold;
    line-height: 1;
    /* Align icon better with text */
}

/* --- Link Styling --- */
a {
    color: #8d6e63;
    /* Dignified brown for links */
    text-decoration: none;
    transition: color 0.3s ease, text-decoration 0.3s ease;
}

a:hover {
    color: #5d4037;
    /* Darker brown on hover */
    text-decoration: underline;
}

.contact-email {
    font-weight: bold;
    font-style: italic;
    /* Emphasize email address */
    text-align: center;
    /* Center the email line */
    margin-top: 25px;
}

/* --- Responsive Design --- */
@media (max-width: 992px) {
    .establishment-container {
        margin: 30px auto;
        padding: 30px;
    }

    .main-heading {
        font-size: 3em;
    }

    .chapter-title {
        font-size: 2em;
    }

    .chapter-section {
        padding: 25px;
    }

    .chapter-title::before {
        left: -30px;
    }
}

@media (max-width: 768px) {
    .establishment-container {
        margin: 20px auto;
        padding: 20px;
    }

    .main-heading {
        font-size: 2.5em;
        margin-bottom: 40px;
    }

    .chapter-title {
        font-size: 1.8em;
    }

    .chapter-paragraph,
    .feature-list li {
        font-size: 1em;
    }

    .chapter-section {
        padding: 20px;
        margin-bottom: 30px;
    }

    .chapter-title::before {
        left: -25px;
        font-size: 0.7em;
    }

    .feature-list li {
        padding-left: 30px;
    }

    .feature-list li .feature-icon {
        font-size: 1.2em;
    }
}
</style>