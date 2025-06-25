<template>
    <div class="establishment-container">
        <h1 class="main-heading">Concerning The Scriptorium: Our Endeavour</h1>

        <section class="chapter-section mission-statement">
            <h2 class="chapter-title">Our Sacred Mission</h2>
            <p class="chapter-paragraph">
                Welcome, esteemed patron, to The Scriptorium – your esteemed guide through the boundless realms of
                literature. Our solemn mission is to aid every ardent reader in discerning their next cherished volume.
                In a world brimming with countless literary treasures, the quest for the perfect narrative can be both
                exhilarating and, at times, daunting. With the wisdom of advanced algorithms and a profound appreciation
                for the nuances of literary taste, we endeavour to present recommendations uniquely tailored to your
                discerning predilections.
            </p>
        </section>

        <section class="chapter-section how-it-works">
            <h2 class="chapter-title">The Mechanics of Our Craft</h2>
            <p class="chapter-paragraph">
                The very fabric of our system is woven with your literary journey at its core. As you engage with our
                platform – by appraising volumes, marking them as perused, or consigning them to your personal ledger of
                desired acquisitions – our discerning engine diligently apprehends your singular reading inclinations.
                We meticulously analyse sundry elements, including your preferred genres, the distinctive styles of
                authors, their publication epochs, and even the very sentiments conveyed within critical appraisals,
                thereby furnishing recommendations of remarkable precision. The more profound your engagement with our
                establishment, the more perspicacious becomes its comprehension of your cultivated literary palate!
            </p>
            <ul class="feature-list">
                <li>
                    <span class="feature-icon">★</span>
                    <strong>Curated Disclosures:</strong> Recommendations bespoke to your reading chronicles and
                    cultivated tastes.
                </li>
                <li>
                    <span class="feature-icon">◆</span>
                    <strong>Diverse Literary Domains:</strong> Traverse the vast expanse from captivating Fictions and
                    profound Non-Fictions to the lyrical expressions of Poesy and the wondrous speculations of the
                    Scientific Romances.
                </li>
                <li>
                    <span class="feature-icon">ↈ</span>
                    <strong>Communal Convocations:</strong> Discern the preferences of fellow literary enthusiasts and
                    graciously impart your own profound insights.
                </li>
                <li>
                    <span class="feature-icon">◊</span>
                    <strong>An Intuitive Compendium:</strong> A seamless and most intuitive experience devised for every
                    devoted bibliophile.
                </li>
            </ul>
        </section>

        <section class="chapter-section our-team">
            <h2 class="chapter-title">The Artisans of This Establishment</h2>
            <p class="chapter-paragraph">
                We are a collective of impassioned developers, sagacious data scientists, and fervent readers, each
                profoundly convinced of the inherent power within the written word. Our combined acumen in machine
                learning, user experience architecting, and the venerable realm of literature fuels our unwavering
                commitment to forge a recommendation system both intelligent in its discernment and truly felicitous in
                its application. We incessantly strive to refine our algorithms and augment our ever-expanding
                repository of tomes, ensuring you shall perpetually encounter fresh and beguiling discoveries.
            </p>
        </section>

        <section class="chapter-section contact-us">
            <h2 class="chapter-title">Making Your Acquaintance</h2>
            <p class="chapter-paragraph">
                We are ever eager to lend an attentive ear to the esteemed voices of our patrons! Should you possess any
                queries, commendations, or sage counsel, pray, do not hesitate to make contact. Your invaluable
                observations serve to perpetually refine and elevate The Scriptorium.
            </p>
            <p class="chapter-paragraph contact-email">
                One may address us via correspondence:
                <a href="mailto:curator@thescriptorium.com">curator@thescriptorium.com</a>
            </p>
        </section>

        <section class="chapter-section acknowledgements">
            <h2 class="chapter-title">A Word of Gratitude</h2>
            <p class="chapter-paragraph">
                Our profound thanks are extended to the venerable open-source fraternities and the various purveyors of
                data, whose invaluable resources proved instrumental in the very construction and perpetual enhancement
                of this cherished platform.
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