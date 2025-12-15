import matplotlib.pyplot as plt
import numpy as np

def draw_plasmid_final():
    total_bp = 5313
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw={'projection': 'polar'})
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    
    # ניקוי הרקע
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.spines['polar'].set_visible(False)
    ax.grid(False)

    # 1. ציור המעגל (Backbone)
    ax.plot(np.linspace(0, 2*np.pi, 100), [1]*100, color='silver', linewidth=3)

    # 2. ציור ה-Insert
    insert_start = 470
    insert_end = 2352
    theta_range = np.linspace(2*np.pi*insert_start/total_bp, 2*np.pi*insert_end/total_bp, 100)
    ax.plot(theta_range, [1]*100, color='dodgerblue', linewidth=8, label='Insert')

    # פונקציה חכמה להוספת תוויות עם חצים (Annotations)
    def add_arrow_label(name, pos, text_pos_deg=None, offset_r=0.2, color='black', fontsize=9):
        # זווית אמיתית של האתר (ברדיאנים)
        theta_real = 2 * np.pi * pos / total_bp
        
        # אם לא הגדרנו מיקום ידני לטקסט, הוא יהיה באותה זווית כמו האתר
        if text_pos_deg is None:
            theta_text = theta_real
            r_text = 1 + offset_r
        else:
            # המרת המיקום הידני לרדיאנים (0 למעלה, עם כיוון השעון)
            # Matplotlib polar מצפה לרדיאנים. 
            # המרה מזווית "שעון" לזווית מתמטית בפולאר:
            theta_text = np.radians(text_pos_deg)

        # שימוש ב-annotate כדי למתוח חץ מהטקסט לנקודה
        ax.annotate(
            f"{name}\n({pos})",
            xy=(theta_real, 1),            # הנקודה על המעגל
            xytext=(theta_text, 1 + offset_r), # איפה הטקסט יושב
            textcoords='polar',
            arrowprops=dict(arrowstyle="-", color=color, linewidth=0.8), # קו דק
            horizontalalignment='center',
            verticalalignment='center',
            color=color,
            fontsize=fontsize,
            fontweight='bold'
        )

    # --- פתרון הצפיפות (הפרדה ידנית של הזוויות לטקסט בלבד) ---
    
    # BamHI (440): נזיז את הטקסט "אחורה" (נגד כיוון השעון) לזווית 20 מעלות
    add_arrow_label("BamHI", 440, text_pos_deg=20, offset_r=0.25, fontsize=8)

    # NotI (452): נשאיר באמצע, בזווית 30 מעלות (בערך המיקום האמיתי), אבל גבוה יותר
    add_arrow_label("NotI", 452, text_pos_deg=30, offset_r=0.35, fontsize=8)

    # Start Insert (470): נזיז את הטקסט "קדימה" (עם כיוון השעון) לזווית 45 מעלות
    add_arrow_label("Start Insert", 470, text_pos_deg=45, offset_r=0.25, color='blue', fontsize=9)


    # --- שאר האתרים (ללא בעיית צפיפות) ---
    add_arrow_label("XhoI", 2, offset_r=0.15)
    add_arrow_label("PvuII", 1129, offset_r=0.15, color='blue')
    add_arrow_label("HindIII", 2179, offset_r=0.15, color='blue')
    add_arrow_label("End Insert", 2352, offset_r=0.15, color='blue')
    add_arrow_label("XbaI", 3241, offset_r=0.15)
    
    # אלמנטים כלליים
    ax.text(np.radians(340), 1.15, "Promoter", ha='center', color='green', fontsize=8)
    ax.text(np.radians(270), 1.15, "AmpR / Ori", ha='center', color='gray', fontsize=8)

    plt.title(f"Recombinant Plasmid Map\n({total_bp} bp)", y=1.1)
    plt.show()

draw_plasmid_final()