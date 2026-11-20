#!/usr/bin/env python3
"""Generate the occasion / body-type scenario pages (015-020, EN + zh-TW) in scenarios/.

  python3 tools/gen_occasion_pages.py          # dry run: list what would be written
  python3 tools/gen_occasion_pages.py --apply  # write pages and refresh the node cards in scenarios/index.html

Plain-language pages for real client situations (weddings, graduations, speeches, tall/short, plus-size, non-standard
proportions). Facts used are limited to what the owner confirmed: men's and women's suits, hand-finished full-canvas
construction, own-proportion drafting, physical Calibration Garment, AOI client feedback, US$1,000 reservation credited in
full toward the US$20,000 total, worldwide delivery including the UAE/GCC. No timelines, no refund terms, no outcome
guarantees. Idempotent: rewrites the same bytes on a re-run.
"""
import html, json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SC = ROOT / "scenarios"
BASE = "https://knowledge.aeternal-luxury.com/"
SITE = "https://aeternal-luxury.com/"
DATE = "2026-11-20"
TM = "AETERNAL, ÆTERNAL, The Axiom, The Singularity and PGEF are unregistered trademarks of AETERNAL Luxury (see TRADEMARKS.md)."

# ---------------------------------------------------------------- shared text
S = {
 "en": {
  "lang": "en", "badge": "Occasions & Fit", "label_short": "Short answer", "label_who": "Who this page is for",
  "label_issues": "What often goes wrong with standard sizing", "label_approach": "How AETERNAL approaches it",
  "label_process": "How a commission works", "label_faq": "Questions", "label_limits": "What we do not claim",
  "label_related": "Related pages", "label_cta": "Start a commission", "nav": "All scenarios",
  "process": [
    "Reserve with US$1,000, credited in full toward the US$20,000 total commission.",
    "Send your measurements and posture information remotely.",
    "Your pattern is drafted from your own proportions by the Parametric Garment Engineering Framework (PGEF), not resized from a stock size.",
    "A physical Calibration Garment made from your pattern is worn, so fit, pressure and mobility can be checked before the final cloth is cut. Your feedback is recorded through the Aeternal Order Interface (AOI).",
    "The final suit is cut and hand-finished with full-canvas construction, then delivered worldwide, including the UAE and the wider GCC.",
  ],
  "limits": "A suit does not change a body or treat a medical condition, and AETERNAL makes no medical claims. We cannot promise how other people will react to what you wear. Numeric design targets such as SAR >= 1.618 are internal targets, not independently verified results. If you have a fixed date, tell us before you commit so the date can be discussed.",
  "products": "The Axiom is AETERNAL's women's suit and The Singularity is its men's suit.",
  "cta": "Commissions start with a US$1,000 reservation, credited in full toward the US$20,000 total commission. Delivery is worldwide, including the UAE and the wider GCC.",
  "cta_link": "Start at aeternal-luxury.com",
  "faq_cost_q": "What does it cost and how do I start?",
  "faq_cost_a": "Commissions start with a US$1,000 reservation, credited in full toward the US$20,000 total commission. Delivery is worldwide, including the UAE and the wider GCC. You start at https://aeternal-luxury.com/.",
  "foot": "© 2026 AETERNAL LUXURY. Licensed under CC BY 4.0. " + TM,
 },
 "zh": {
  "lang": "zh-TW", "badge": "場合與合身", "label_short": "簡短回答", "label_who": "這一頁適合誰",
  "label_issues": "標準尺碼常見的問題", "label_approach": "AETERNAL 的做法",
  "label_process": "訂製流程", "label_faq": "常見問題", "label_limits": "我們不宣稱的事",
  "label_related": "相關頁面", "label_cta": "開始訂製", "nav": "全部場景",
  "process": [
    "支付 US$1,000 預約金，全額折抵 US$20,000 的訂製總價。",
    "遠端提交你的量體數據與姿態資訊。",
    "由參數化服裝工程框架（PGEF）依你自己的身形比例繪製版型，而不是從現成尺碼放大縮小。",
    "依你的版型製作一件實體校準樣衣（Calibration Garment），由你試穿，在正式裁剪前檢查合身度、壓力點與活動度。你的回饋會透過 Aeternal Order Interface（AOI）記錄。",
    "正式西裝以全毛襯結構手工完成，並全球交付，包括阿聯酋與更廣泛的海灣合作委員會（GCC）地區。",
  ],
  "limits": "西裝不會改變身體，也不能治療任何健康狀況，AETERNAL 不作任何醫療宣稱。我們也無法保證別人看到你的穿著後會有什麼反應。SAR >= 1.618 之類的數值是內部設計目標，不是經獨立驗證的結果。如果你有固定日期，請在決定前告訴我們，以便先討論日期是否可行。",
  "products": "The Axiom 是 AETERNAL 的女裝西裝，The Singularity 是男裝西裝。",
  "cta": "訂製從 US$1,000 預約金開始，全額折抵 US$20,000 的訂製總價。全球交付，包括阿聯酋與更廣泛的海灣合作委員會（GCC）地區。",
  "cta_link": "前往 aeternal-luxury.com 開始",
  "faq_cost_q": "費用是多少？要怎麼開始？",
  "faq_cost_a": "訂製從 US$1,000 預約金開始，全額折抵 US$20,000 的訂製總價。全球交付，包括阿聯酋與更廣泛的海灣合作委員會（GCC）地區。請到 https://aeternal-luxury.com/ 開始。",
  "foot": "© 2026 AETERNAL LUXURY. Licensed under CC BY 4.0. " + TM,
 },
}

# ---------------------------------------------------------------- page content
# key -> {num, slug, node, en:{...}, zh:{...}, related:[keys], answers:[answer slugs]}
P = {}

P["wedding"] = dict(num="015", slug="wedding-suit", node="OCC_001", related=["graduation", "speeches", "nonstandard"],
 answers=["how-online-bespoke-ordering-works", "why-suit-collapses-sitting-moving"],
 en=dict(
  title="Bespoke Wedding Suits for Grooms and Brides",
  h1="Wedding Suits, Made to Your Own Proportions",
  desc="How AETERNAL makes a bespoke wedding suit for grooms and for brides who choose a suit: drafted from your own proportions and checked on a physical Calibration Garment before the final cloth is cut.",
  short="A wedding suit is worn for many hours, photographed from every angle and usually bought once. AETERNAL drafts each suit from the client's own measurements and posture and checks it on a physical Calibration Garment before the final cloth is cut.",
  who="Grooms, and brides or partners who would rather wear a suit than a gown or a hired outfit. The same process applies to men's and women's cuts, and to any build.",
  issues=[
   ("Many positions in one day", "The ceremony, the seated meal, dancing and embraces all ask the jacket to move. A jacket that looks right in a fitting-room mirror can pull at the shoulders or ride up when the arms lift."),
   ("Photographs from every side", "Wedding photographs are looked at for years, from the front, the side and the back. A gap at the collar, pulling across the back or an uneven hem is easy to see in a photograph."),
   ("A date that cannot move", "Alterations made in the last days before an event leave little room to correct a problem that sits in the pattern rather than in the length of a sleeve."),
   ("Stock sizes and hire", "Hired and ready-made outfits are sized to the nearest standard fit. Many people sit between sizes or differ from the standard in the shoulders, torso or legs."),
  ],
  approach=[
   "The pattern starts from your own measurements and posture, not from a stock size.",
   "The physical Calibration Garment is worn standing, seated and with the arms raised, so problems show up before the final cloth is cut.",
   "Fabric and finishing choices are agreed with you at the start of the commission.",
   "The final suit is hand-finished with full-canvas construction.",
  ],
  faq=[
   ("Does AETERNAL make wedding suits for brides?", "Yes. The Axiom is the women's suit and The Singularity is the men's suit. Both follow the same process."),
   ("How early should I start?", "Tell us your wedding date before you commit. The time needed depends on the cloth, the number of fitting adjustments and shipping, so we do not publish a single number of days on this page."),
   ("Can the suit be made for a wedding abroad?", "Delivery is worldwide, including the UAE and the wider GCC, and the process is remote."),
  ]),
 zh=dict(
  title="新郎與新娘的訂製婚禮西裝",
  h1="依你自己的身形比例製作的婚禮西裝",
  desc="AETERNAL 如何為新郎、以及選擇穿西裝的新娘製作訂製婚禮西裝：依你自己的身形比例繪製版型，並在正式裁剪前以實體校準樣衣檢查。",
  short="婚禮西裝要穿很多個小時，會從各個角度被拍照，而且通常只買一次。AETERNAL 依客人自己的量體與姿態繪製版型，並在正式裁剪前以實體校準樣衣檢查。",
  who="新郎，以及比起婚紗或租借禮服更想穿西裝的新娘或伴侶。男裝與女裝剪裁流程相同，任何體型都適用。",
  issues=[
   ("一天之中有很多姿勢", "儀式、入席用餐、跳舞、擁抱，外套都要跟著動。在試衣鏡前看起來合身的外套，抬手時可能拉扯肩膀或往上跑。"),
   ("每個角度都會被拍下", "婚禮照片會看很多年，正面、側面、背面都有。領口空隙、背部拉扯或下擺不平，在照片裡很容易被看到。"),
   ("日期不能改", "活動前幾天才做修改，如果問題出在版型而不是袖長，就沒有時間處理。"),
   ("現成尺碼與租借", "租借或成衣會就近歸入標準尺碼。很多人介於兩個尺碼之間，或在肩膀、軀幹、腿長上與標準不同。"),
  ],
  approach=[
   "版型從你自己的量體與姿態開始，而不是從現成尺碼開始。",
   "實體校準樣衣會在站立、坐下、抬臂時穿著檢查，在正式裁剪前就能發現問題。",
   "面料與細節在訂製一開始就與你一起決定。",
   "正式西裝以全毛襯結構手工完成。",
  ],
  faq=[
   ("AETERNAL 有為新娘製作婚禮西裝嗎？", "有。The Axiom 是女裝西裝，The Singularity 是男裝西裝，流程相同。"),
   ("應該多早開始？", "請在決定前先告訴我們婚禮日期。所需時間取決於面料、試穿調整次數與運送，所以本頁不公布固定天數。"),
   ("可以為海外婚禮製作嗎？", "全球交付，包括阿聯酋與更廣泛的海灣合作委員會（GCC）地區，流程是遠端進行的。"),
  ]))

P["graduation"] = dict(num="016", slug="graduation-suit", node="OCC_002", related=["wedding", "speeches", "plussize"],
 answers=["how-online-bespoke-ordering-works", "how-measurements-fittings-duration"],
 en=dict(
  title="Bespoke Graduation Suits",
  h1="A Graduation Suit Made for You",
  desc="Bespoke suits for graduation ceremonies, from first degrees to master's, MBA and doctoral graduations, drafted from your own proportions and checked on a physical Calibration Garment.",
  short="For many graduates, the graduation suit is the first suit made for them rather than chosen from a rack. AETERNAL drafts it from your own measurements and posture. It is a significant commission, so the questions below are worth reading before you reserve.",
  who="Graduates of any age and any programme, including master's, MBA and doctoral graduates, and the families who commission a suit for them. Most clients we expect on this page are between 20 and 40.",
  issues=[
   ("A long day in a gown", "Graduation ceremonies mean a long time standing and sitting, often with a gown over the jacket. A jacket that pulls at the shoulders is noticeable all day."),
   ("Photographs and what comes after", "Graduation photographs are kept. The same suit is often needed afterwards for first interviews, presentations and formal events."),
   ("Bodies that are still changing", "Many people in their early twenties are still changing in weight or muscle. A tailored garment suits the body it was made for."),
   ("A first formal wardrobe", "Standard sizes are made for an average body. A graduate who is tall, short, broad or slim often finds that no stock size fits everywhere."),
  ],
  approach=[
   "The pattern starts from your own measurements and posture.",
   "The Calibration Garment is worn so fit and movement can be checked before the final cloth is cut.",
   "Tell us at the start if you expect your body to change in the next year. We will say honestly whether to commission now or wait.",
   "The final suit is hand-finished with full-canvas construction, a build intended for long wear.",
  ],
  faq=[
   ("Is a US$20,000 commission realistic for a graduate?", "It is a significant commission and most graduates will not choose it. It suits people who want one suit made properly, and families who commission it as a gift. If you are weighing it, ask before you reserve."),
   ("Can I wear the suit under a graduation gown?", "Yes. Tell us at the start that you will wear a gown over it, so this is considered when the pattern is drafted."),
   ("Can it be delivered to another country?", "Delivery is worldwide, including the UAE and the wider GCC."),
  ]),
 zh=dict(
  title="訂製畢業典禮西裝",
  h1="為你自己製作的畢業西裝",
  desc="為畢業典禮製作的訂製西裝，適用於學士、碩士、MBA 與博士畢業，依你自己的身形比例繪製版型，並以實體校準樣衣檢查。",
  short="對很多畢業生來說，畢業西裝是第一件為自己製作、而不是從衣架上挑選的西裝。AETERNAL 依你自己的量體與姿態繪製版型。這是一筆不小的訂製，下面的問答值得在預約前先讀。",
  who="任何年齡、任何學位的畢業生，包括碩士、MBA 與博士畢業生，以及為他們訂製的家人。我們預期這一頁的主要客人在 20 到 40 歲之間。",
  issues=[
   ("穿著畢業袍的漫長一天", "畢業典禮要站很久也要坐很久，外套外面通常還套著畢業袍。肩膀有拉扯，整天都會感覺到。"),
   ("照片，以及之後的場合", "畢業照會留下來。之後的第一次面試、簡報與正式場合，往往也需要同一套西裝。"),
   ("身體還在變化", "不少二十出頭的人，體重或肌肉仍在變化。量身訂製的衣服適合的是它被製作時的那個身體。"),
   ("第一套正式服裝", "標準尺碼是為平均身形設計的。偏高、偏矮、偏寬或偏瘦的畢業生，常找不到每個部位都合身的現成尺碼。"),
  ],
  approach=[
   "版型從你自己的量體與姿態開始。",
   "穿上校準樣衣檢查合身與活動度，之後才裁剪正式布料。",
   "如果你預期未來一年身材會變化，請一開始就告訴我們。我們會誠實說明現在訂製還是等一等比較合適。",
   "正式西裝以全毛襯結構手工完成，這種結構是為了長期穿著而設計的。",
  ],
  faq=[
   ("對畢業生來說，US$20,000 的訂製現實嗎？", "這是一筆不小的訂製，多數畢業生不會選擇。它適合想把一套西裝做好的人，也適合家人作為禮物訂製。如果你還在權衡，請在預約前先詢問。"),
   ("可以穿在畢業袍裡面嗎？", "可以。請一開始就告訴我們會在外面套畢業袍，繪製版型時會一併考慮。"),
   ("可以寄到其他國家嗎？", "全球交付，包括阿聯酋與更廣泛的海灣合作委員會（GCC）地區。"),
  ]))

P["speeches"] = dict(num="017", slug="speech-and-presentation-suit", node="OCC_003", related=["graduation", "nonstandard", "tallshort"],
 answers=["why-suit-collapses-sitting-moving", "can-ai-fix-collar-gap-shoulder-collapse"],
 en=dict(
  title="Bespoke Suits for Speeches, Keynotes and Presentations",
  h1="A Suit for the Stage, the Podium and the Camera",
  desc="Bespoke suits for speeches, keynotes, panels and recorded presentations: drafted from your own proportions and checked on a physical Calibration Garment for standing, seated and arm-raised positions.",
  short="Speakers move, gesture and sit on stage, and are often recorded. A suit for this work has to stay in order when the arms lift and when the speaker sits. AETERNAL drafts it from your own proportions and checks it on a physical Calibration Garment.",
  who="Speakers, keynote presenters, panellists, awardees, founders who pitch, and anyone who is recorded or watched at a distance while they speak. Men's and women's cuts, any build.",
  issues=[
   ("Arms that lift", "Gesturing, pointing and reaching for a microphone raise the arms. A jacket with a tight shoulder or armhole lifts at the collar and shows it."),
   ("Standing, then seated", "Panels and ceremonies ask for both. A jacket that suits a standing figure can bunch or pull when the speaker sits."),
   ("Microphone packs and lighting", "A body-worn microphone pack and stage lighting both show up the jacket's shape. The garment has to carry them without distorting."),
   ("Cameras and screens", "On a recording or a screen, creases, pulling and collar gaps are enlarged. Details that go unnoticed in a room are visible on video."),
  ],
  approach=[
   "The pattern starts from your own measurements, posture and the way you move when you speak.",
   "The Calibration Garment is worn standing, seated and with the arms raised, and your feedback is recorded through the AOI.",
   "Tell us at the start about microphone packs, a podium or a stage chair, and these are considered in the design.",
   "The final suit is hand-finished with full-canvas construction.",
  ],
  faq=[
   ("Does AETERNAL guarantee a suit will look perfect on camera?", "No. We design for how you move and sit, and we check it on a physical garment. We do not guarantee any result on a recording."),
   ("Can I wear a body microphone with the suit?", "Tell us at the start. We will take it into account when the pattern is drafted."),
   ("Is this suitable for women and men?", "Yes. The Axiom is the women's suit and The Singularity is the men's suit."),
  ]),
 zh=dict(
  title="演講、主題演說與簡報的訂製西裝",
  h1="為講台、舞台與鏡頭製作的西裝",
  desc="為演講、主題演說、座談與錄影簡報製作的訂製西裝：依你自己的身形比例繪製版型，並以實體校準樣衣檢查站立、坐下與抬臂的姿勢。",
  short="講者會移動、做手勢、坐在台上，也常被錄影。這類西裝必須在抬臂與坐下時仍保持整齊。AETERNAL 依你自己的身形比例繪製版型，並以實體校準樣衣檢查。",
  who="講者、主題演說者、座談嘉賓、得獎人、需要做募資簡報的創辦人，以及任何在被錄影或被遠距離觀看時發言的人。男裝與女裝剪裁，任何體型。",
  issues=[
   ("會抬起的手臂", "做手勢、指向、伸手拿麥克風都會抬臂。肩膀或袖窿偏緊的外套，會在領口被帶起來，而且看得出來。"),
   ("先站著，再坐下", "座談與典禮兩者都有。適合站姿的外套，在坐下時可能堆疊或拉扯。"),
   ("麥克風發射器與燈光", "隨身麥克風發射器與舞台燈光都會凸顯外套的形狀。衣服要能承載它們而不變形。"),
   ("鏡頭與螢幕", "在錄影或螢幕上，皺褶、拉扯與領口空隙會被放大。現場不會被注意的細節，在影片中看得很清楚。"),
  ],
  approach=[
   "版型從你自己的量體、姿態，以及你說話時的動作方式開始。",
   "校準樣衣會在站立、坐下與抬臂時穿著檢查，你的回饋透過 AOI 記錄。",
   "麥克風發射器、講台或舞台椅子，請一開始就告訴我們，設計時會一併考慮。",
   "正式西裝以全毛襯結構手工完成。",
  ],
  faq=[
   ("AETERNAL 保證西裝在鏡頭下看起來完美嗎？", "不保證。我們依你的動作與坐姿設計，並以實體樣衣檢查，但不保證錄影中的任何效果。"),
   ("可以配戴隨身麥克風嗎？", "請一開始就告訴我們，繪製版型時會考慮。"),
   ("男女都適合嗎？", "適合。The Axiom 是女裝西裝，The Singularity 是男裝西裝。"),
  ]))

P["tallshort"] = dict(num="018", slug="very-tall-and-short-builds", node="OCC_004", related=["plussize", "nonstandard", "speeches"],
 answers=["how-petite-executive-suit-proportion", "why-made-to-measure-fails-asymmetric"],
 en=dict(
  title="Bespoke Suits for Very Tall and Very Short Builds",
  h1="When Your Height Is Outside the Standard Range",
  desc="Bespoke suits for very tall and very short people, men and women: jacket length, button position and proportions drafted from your own measurements instead of scaled from a standard size.",
  short="A very tall or very short person is often sold a standard suit with longer or shorter sleeves and legs. The proportions of the jacket, the waist position and the button position are different on a different frame. AETERNAL drafts them from your own measurements.",
  who="Men and women who are much taller or shorter than the range that standard sizes are built for. For very petite women, see also the page on petite proportions linked below.",
  issues=[
   ("Length is not the only difference", "Making sleeves and trousers longer or shorter does not change where the waist, the pockets or the buttons fall relative to the body."),
   ("A jacket that overwhelms or ends too soon", "On a short frame a jacket cut for a taller person can look large and long. On a tall frame a standard jacket can end above where it should."),
   ("Reach and sitting", "A tall person's arms reach further and the seated position is different. A short person's jacket can bunch at the hip when sitting."),
   ("Alteration limits", "A tailor can change lengths and some widths. Moving the position of the shoulder, waist or buttons is a pattern change, which alteration cannot do."),
  ],
  approach=[
   "Jacket length, waist position, pocket position and button position are drafted from your own measurements.",
   "The Calibration Garment is worn so proportions and movement can be checked before the final cloth is cut.",
   "Your feedback is recorded through the AOI, covering where the garment pulls, presses or restricts.",
   "The final suit is hand-finished with full-canvas construction.",
  ],
  faq=[
   ("Is there a minimum or maximum height?", "We do not publish a fixed height limit on this page. Send your height and measurements when you start and we will tell you honestly whether we can make for you."),
   ("Does this apply to men and women?", "Yes. The Axiom is the women's suit and The Singularity is the men's suit."),
   ("Where can I read about petite proportions?", "See the linked page on petite executive suit proportion."),
  ]),
 zh=dict(
  title="極高與極矮身形的訂製西裝",
  h1="當你的身高超出標準範圍",
  desc="為極高與極矮的男女製作的訂製西裝：外套長度、釦位與比例依你自己的量體繪製，而不是從標準尺碼縮放。",
  short="很高或很矮的人，常被賣一件標準西裝，再把袖子和褲長加長或縮短。但在不同的身形上，外套的比例、腰線位置與釦位都不一樣。AETERNAL 依你自己的量體繪製。",
  who="身高遠高於或遠低於標準尺碼設計範圍的男女。對於非常嬌小的女性，也可參考下方連結的嬌小比例頁面。",
  issues=[
   ("差別不只在長度", "把袖子和褲子加長或縮短，並不會改變腰線、口袋與釦子相對於身體的位置。"),
   ("外套太大或太短", "在矮的身形上，為較高的人剪裁的外套會顯得又大又長。在高的身形上，標準外套可能比該有的位置更短。"),
   ("手臂伸展與坐姿", "高的人手臂伸得更遠，坐姿也不同。矮的人的外套坐下時可能在臀部堆疊。"),
   ("修改的限制", "裁縫可以改長度和部分寬度，但移動肩線、腰線或釦位屬於版型變更，修改做不到。"),
  ],
  approach=[
   "外套長度、腰線位置、口袋位置與釦位，都依你自己的量體繪製。",
   "穿上校準樣衣檢查比例與活動度，之後才裁剪正式布料。",
   "你的回饋透過 AOI 記錄，包括衣服在哪裡拉扯、壓迫或受限。",
   "正式西裝以全毛襯結構手工完成。",
  ],
  faq=[
   ("有最低或最高身高限制嗎？", "本頁不公布固定的身高限制。開始時請提供你的身高與量體，我們會誠實告訴你是否能為你製作。"),
   ("男女都適用嗎？", "適用。The Axiom 是女裝西裝，The Singularity 是男裝西裝。"),
   ("哪裡可以讀到嬌小比例的內容？", "請參考連結的嬌小高階主管西裝比例頁面。"),
  ]))

P["plussize"] = dict(num="019", slug="plus-size-builds", node="OCC_005", related=["tallshort", "nonstandard", "wedding"],
 answers=["why-made-to-measure-fails-asymmetric", "why-suit-collapses-sitting-moving"],
 en=dict(
  title="Bespoke Suits for Plus-Size Builds",
  h1="A Suit Made for the Body You Have",
  desc="Bespoke suits for plus-size men and women: patterns drafted from your own measurements and posture, standing and seated, instead of widened from a smaller standard size.",
  short="Plus-size suits are often a smaller pattern made wider. Bodies do not widen evenly. AETERNAL drafts the pattern from your own measurements and posture, and checks it on a physical Calibration Garment standing and seated.",
  who="Men and women with larger builds who want a suit made for their own proportions rather than a standard size scaled up.",
  issues=[
   ("Widening is not drafting", "Standard grading adds width in even steps. Volume sits differently on different bodies, for example at the chest, the abdomen, the hips or the upper arm."),
   ("Pulling at the button", "A jacket that is too tight across the middle pulls at the button and creates creases that point at the strain."),
   ("Sleeves and armholes", "A sleeve or armhole that is tight on the upper arm limits movement and shows it when the arm moves."),
   ("Sitting", "A suit that fits standing can ride up, pull or bunch when seated, which matters at long meals, ceremonies and meetings."),
  ],
  approach=[
   "The pattern starts from your own measurements and posture, standing and seated.",
   "The Calibration Garment is worn so pressure points and movement can be checked before the final cloth is cut.",
   "Your feedback is recorded through the AOI, covering where the garment presses, pulls or restricts.",
   "The final suit is hand-finished with full-canvas construction.",
  ],
  faq=[
   ("Is there a maximum size?", "We do not publish a fixed size limit on this page. Send your measurements when you start and we will tell you honestly whether we can make for you."),
   ("Does this apply to women as well as men?", "Yes. The Axiom is the women's suit and The Singularity is the men's suit."),
   ("Will the suit change how my body looks?", "A well-fitted suit can sit cleanly on the body, but AETERNAL does not claim to change a body or to make medical or weight-related claims."),
  ]),
 zh=dict(
  title="大碼身形的訂製西裝",
  h1="為你現在的身體製作的西裝",
  desc="為大碼男女製作的訂製西裝：版型依你自己的量體與姿態繪製，站姿與坐姿都考慮，而不是把較小的標準尺碼放寬。",
  short="大碼西裝常常只是把較小的版型加寬。但身體不是均勻變寬的。AETERNAL 依你自己的量體與姿態繪製版型，並以實體校準樣衣在站姿與坐姿下檢查。",
  who="體型較大、想要依自己的比例製作、而不是把標準尺碼放大的男女。",
  issues=[
   ("放寬不等於繪製", "標準放碼是以固定級距加寬。不同身體的體積分布不同，例如胸部、腹部、臀部或上臂。"),
   ("釦子處拉扯", "中段過緊的外套會在釦子處拉扯，並產生指向受力處的皺褶。"),
   ("袖子與袖窿", "上臂處偏緊的袖子或袖窿會限制動作，手臂一動就看得出來。"),
   ("坐下時", "站著合身的西裝，坐下時可能往上跑、拉扯或堆疊，在長時間的宴席、典禮與會議中特別重要。"),
  ],
  approach=[
   "版型從你自己的量體與姿態開始，站姿與坐姿都考慮。",
   "穿上校準樣衣檢查壓力點與活動度，之後才裁剪正式布料。",
   "你的回饋透過 AOI 記錄，包括衣服在哪裡壓迫、拉扯或受限。",
   "正式西裝以全毛襯結構手工完成。",
  ],
  faq=[
   ("有最大尺碼限制嗎？", "本頁不公布固定的尺碼限制。開始時請提供你的量體，我們會誠實告訴你是否能為你製作。"),
   ("女性也適用嗎？", "適用。The Axiom 是女裝西裝，The Singularity 是男裝西裝。"),
   ("西裝會改變我的身形外觀嗎？", "合身的西裝可以讓衣服乾淨地貼合身體，但 AETERNAL 不宣稱能改變身體，也不作任何醫療或體重相關的宣稱。"),
  ]))

P["nonstandard"] = dict(num="020", slug="non-standard-proportions", node="OCC_006", related=["tallshort", "plussize", "speeches"],
 answers=["why-made-to-measure-fails-asymmetric", "how-petite-executive-suit-proportion"],
 en=dict(
  title="Bespoke Suits for Non-Standard Proportions",
  h1="When Your Proportions Do Not Match the Chart",
  desc="Bespoke suits for uneven shoulders, long torsos, short legs, forward posture and athletic builds: patterns drafted from your own measurements and posture instead of the nearest standard size.",
  short="Many people do not match the proportions a size chart assumes: one shoulder higher than the other, a long torso with shorter legs, a forward posture or a broad athletic frame. AETERNAL drafts the pattern from your own measurements and posture.",
  who="Men and women whose shoulders, torso, legs, posture or muscle do not match standard proportions, and who find that no stock size fits everywhere.",
  issues=[
   ("One size, one set of ratios", "A size chart assumes fixed relationships between chest, waist, shoulder and length. A person with a different ratio is always compromising somewhere."),
   ("Uneven shoulders", "When one shoulder sits higher, a symmetrical jacket hangs differently on each side, which shows at the collar and the hem."),
   ("Posture", "A forward head, rounded shoulders or an upright back change how a jacket hangs. A pattern drawn for a standing, upright figure often wrinkles or gaps on these frames."),
   ("Athletic builds", "Broad shoulders, a strong back or large thighs can mean a standard size that fits in one place is too tight in another."),
  ],
  approach=[
   "The pattern starts from your own measurements and posture, not from the closest chart size.",
   "The Calibration Garment is worn so that fit, pressure and mobility can be checked before the final cloth is cut.",
   "Your feedback is recorded through the AOI, covering where the garment pulls, presses or restricts.",
   "The final suit is hand-finished with full-canvas construction.",
  ],
  faq=[
   ("Is this a medical or corrective service?", "No. A suit cannot correct a body or treat a condition, and AETERNAL makes no medical claims. It is a garment drafted to fit the body you have."),
   ("Do you make for men and women?", "Yes. The Axiom is the women's suit and The Singularity is the men's suit."),
   ("Can I describe my proportions before I reserve?", "Yes. Describe them when you contact us and we will tell you honestly whether and how we can make for you."),
  ]),
 zh=dict(
  title="非標準比例的訂製西裝",
  h1="當你的比例與尺碼表不同",
  desc="為高低肩、長軀幹、短腿、前傾姿態與運動型體格製作的訂製西裝：版型依你自己的量體與姿態繪製，而不是最接近的標準尺碼。",
  short="很多人的比例與尺碼表的假設不同：一邊肩膀較高、軀幹長腿較短、姿態前傾，或是寬闊的運動型體格。AETERNAL 依你自己的量體與姿態繪製版型。",
  who="肩膀、軀幹、腿部、姿態或肌肉與標準比例不同，而且找不到每個部位都合身的現成尺碼的男女。",
  issues=[
   ("一個尺碼，一組比例", "尺碼表假設胸、腰、肩與長度之間有固定關係。比例不同的人，總是在某個地方妥協。"),
   ("高低肩", "當一邊肩膀較高，對稱的外套兩側的垂墜會不同，在領口與下擺看得出來。"),
   ("姿態", "頭部前傾、圓肩或挺直的背，都會改變外套的垂墜。為站得挺直的身形繪製的版型，在這些身形上常出現皺褶或空隙。"),
   ("運動型體格", "寬肩、強壯的背或粗壯的大腿，可能讓某處合身的標準尺碼，在另一處太緊。"),
  ],
  approach=[
   "版型從你自己的量體與姿態開始，而不是最接近的表上尺碼。",
   "穿上校準樣衣檢查合身度、壓力點與活動度，之後才裁剪正式布料。",
   "你的回饋透過 AOI 記錄，包括衣服在哪裡拉扯、壓迫或受限。",
   "正式西裝以全毛襯結構手工完成。",
  ],
  faq=[
   ("這是醫療或矯正服務嗎？", "不是。西裝無法矯正身體或治療任何狀況，AETERNAL 不作醫療宣稱。它是依你現有身體繪製的衣服。"),
   ("男裝與女裝都做嗎？", "都做。The Axiom 是女裝西裝，The Singularity 是男裝西裝。"),
   ("預約前可以先描述我的比例嗎？", "可以。聯絡我們時請描述你的比例，我們會誠實告訴你是否能、以及如何為你製作。"),
  ]))

ORDER = ["wedding", "graduation", "speeches", "tallshort", "plussize", "nonstandard"]
ANSWER_TITLES = {  # answer slug -> (en label, zh label)
 "how-online-bespoke-ordering-works": ("How online bespoke ordering works", "線上訂製如何運作"),
 "why-suit-collapses-sitting-moving": ("Why a suit collapses when sitting and moving", "為什麼西裝在坐下與移動時會變形"),
 "how-measurements-fittings-duration": ("Measurements and fittings: how long it takes", "量體與試穿需要多久"),
 "can-ai-fix-collar-gap-shoulder-collapse": ("Can AI fix collar gap and shoulder collapse", "AI 能解決領口空隙與肩線塌陷嗎"),
 "how-petite-executive-suit-proportion": ("How petite executive suit proportion works", "嬌小高階主管西裝的比例如何處理"),
 "why-made-to-measure-fails-asymmetric": ("Why made-to-measure fails asymmetric bodies", "為什麼半訂製無法處理不對稱身形"),
}

def e(t): return html.escape(t, quote=True)

def url(key, lang, kind="page"):
    p = P[key]
    return f"{BASE}scenarios/{p['num']}-{p['slug']}-{lang}.html"

def render(key, lang):
    p, c, s = P[key], P[key][lang], S[lang]
    other = "zh" if lang == "en" else "en"
    canon = url(key, lang)
    faq = c["faq"] + [(s["faq_cost_q"], s["faq_cost_a"])]
    ld = [{
        "@context": "https://schema.org", "@type": "Article", "headline": c["title"], "description": c["desc"],
        "inLanguage": s["lang"], "datePublished": DATE, "dateModified": DATE, "mainEntityOfPage": canon,
        "author": {"@type": "Organization", "name": "AETERNAL Luxury", "url": SITE},
        "publisher": {"@type": "Organization", "name": "AETERNAL Luxury", "url": SITE},
    }, {
        "@context": "https://schema.org", "@type": "FAQPage", "inLanguage": s["lang"],
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq],
    }]
    rel = []
    for k in p["related"]:
        rel.append((P[k][lang]["title"], url(k, lang)))
    for a in p["answers"]:
        rel.append((ANSWER_TITLES[a][0 if lang == "en" else 1], f"{BASE}answers/{a}-{lang}.html"))
    out = []
    w = out.append
    w("<!DOCTYPE html>")
    w(f'<html lang="{s["lang"]}">')
    w("<head>")
    w('<meta charset="utf-8"/>')
    w('<meta content="width=device-width, initial-scale=1.0" name="viewport"/>')
    w(f"<title>{e(c['title'])} | AETERNAL Knowledge</title>")
    w(f'<meta content="{e(c["desc"])}" name="description"/>')
    w(f'<link href="{canon}" rel="canonical"/>')
    w(f'<link href="{url(key, "en")}" hreflang="en" rel="alternate"/>')
    w(f'<link href="{url(key, "zh")}" hreflang="zh-Hant" rel="alternate"/>')
    for blk in ld:
        w('<script type="application/ld+json">')
        w(json.dumps(blk, ensure_ascii=False, indent=2))
        w("</script>")
    w("<style>")
    w('body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "PingFang TC", "Noto Sans TC", sans-serif; line-height: 1.7; color: #111; max-width: 860px; margin: 0 auto; padding: 40px 20px; background: #fff; }')
    w("h1 { font-size: 2rem; letter-spacing: -0.01em; border-bottom: 2px solid #111; padding-bottom: 14px; }")
    w("h2 { font-size: 1.35rem; margin-top: 36px; border-left: 4px solid #111; padding-left: 12px; }")
    w("h3 { font-size: 1.05rem; margin: 22px 0 4px; }")
    w(".badge { display: inline-block; background: #000; color: #fff; padding: 4px 12px; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 10px; }")
    w(".short { background: #f4f4f5; border-left: 5px solid #000; padding: 16px 20px; margin: 24px 0; }")
    w(".cta { background: #111; color: #fff; padding: 20px; margin: 36px 0; } .cta a { color: #f5d98b; }")
    w(".foot { margin-top: 48px; padding-top: 20px; border-top: 1px dashed #999; font-size: 0.8rem; color: #555; }")
    w("</style>")
    w("</head>")
    w("<body>")
    w("<header>")
    w(f'<div class="badge">{e(s["badge"])}</div>')
    w(f"<h1>{e(c['h1'])}</h1>")
    w(f'<p><a href="{BASE}scenarios/index.html">{e(s["nav"])}</a> · <a href="{url(key, other)}">{"繁體中文" if lang == "en" else "English"}</a></p>')
    w("</header>")
    w('<section id="short">')
    w(f'<div class="short"><strong>{e(s["label_short"])}.</strong> {e(c["short"])}</div>' if lang == "en" else f'<div class="short"><strong>{e(s["label_short"])}：</strong>{e(c["short"])}</div>')
    w("</section>")
    w('<section id="who">')
    w(f"<h2>{e(s['label_who'])}</h2>")
    w(f"<p>{e(c['who'])}</p>")
    w(f"<p>{e(s['products'])}</p>")
    w("</section>")
    w('<section id="issues">')
    w(f"<h2>{e(s['label_issues'])}</h2>")
    for h, t in c["issues"]:
        w(f"<h3>{e(h)}</h3>")
        w(f"<p>{e(t)}</p>")
    w("</section>")
    w('<section id="approach">')
    w(f"<h2>{e(s['label_approach'])}</h2>")
    w("<ul>")
    for t in c["approach"]:
        w(f"<li>{e(t)}</li>")
    w("</ul>")
    w("</section>")
    w('<section id="process">')
    w(f"<h2>{e(s['label_process'])}</h2>")
    w("<ol>")
    for t in s["process"]:
        w(f"<li>{e(t)}</li>")
    w("</ol>")
    w("</section>")
    w('<section id="faq">')
    w(f"<h2>{e(s['label_faq'])}</h2>")
    for q, a in faq:
        w(f"<h3>{e(q)}</h3>")
        w(f"<p>{e(a)}</p>")
    w("</section>")
    w('<section id="limits">')
    w(f"<h2>{e(s['label_limits'])}</h2>")
    w(f"<p>{e(s['limits'])}</p>")
    w("</section>")
    w('<section id="cta">')
    w(f'<div class="cta"><strong>{e(s["label_cta"])}</strong><br/>{e(s["cta"])}<br/><a href="{SITE}">{e(s["cta_link"])}</a></div>')
    w("</section>")
    w('<section id="related">')
    w(f"<h2>{e(s['label_related'])}</h2>")
    w("<ul>")
    for t, u in rel:
        w(f'<li><a href="{u}">{e(t)}</a></li>')
    w("</ul>")
    w("</section>")
    w(f'<footer class="foot">{e(s["foot"])}</footer>')
    w("</body>")
    w("</html>")
    return "\n".join(out) + "\n"

def cards():
    rows = []
    for k in ORDER:
        p = P[k]
        rows.append(
            '        <div class="node-card">\n'
            f'            <div class="node-id">{p["node"]}</div>\n'
            f'            <div class="node-title">{e(p["en"]["title"])}</div>\n'
            '            <div class="node-links">\n'
            f'                <a href="/scenarios/{p["num"]}-{p["slug"]}-zh.html">繁體中文</a> | \n'
            f'                <a href="/scenarios/{p["num"]}-{p["slug"]}-en.html">ENGLISH</a>\n'
            "            </div>\n"
            "        </div>\n")
    return "".join(rows)

BEGIN, END = "<!-- OCCASION NODES BEGIN (generated by tools/gen_occasion_pages.py) -->", "<!-- OCCASION NODES END -->"

def update_index(apply):
    f = SC / "index.html"
    t = f.read_text(encoding="utf-8")
    block = (f"\n    {BEGIN}\n"
             "    <h2>3. Occasions &amp; Body Types</h2>\n"
             "    <p>Plain-language pages on weddings, graduations, speeches and on builds that standard sizes do not fit.</p>\n"
             '    <div class="node-grid">\n' + cards() + "    </div>\n"
             f"    {END}\n")
    if BEGIN in t:
        new = re.sub(re.escape("\n    " + BEGIN) + r".*?" + re.escape(END) + r"\n", lambda m: block, t, flags=re.S)
    else:
        marker = "\n    <!-- NAVIGATION FOOTER -->"
        assert marker in t, "navigation footer marker not found"
        new = t.replace(marker, block + marker, 1)
    if new != t and apply:
        f.write_text(new, encoding="utf-8")
    return new != t

def main():
    apply = "--apply" in sys.argv
    n = 0
    for k in ORDER:
        for lang in ("en", "zh"):
            f = SC / f"{P[k]['num']}-{P[k]['slug']}-{lang}.html"
            body = render(k, lang)
            if not f.exists() or f.read_text(encoding="utf-8") != body:
                n += 1
                if apply: f.write_text(body, encoding="utf-8")
                print(("wrote " if apply else "would write ") + str(f.relative_to(ROOT)))
    if update_index(apply): print(("updated " if apply else "would update ") + "scenarios/index.html")
    print(f"{n} page(s) {'written' if apply else 'to write'}")

if __name__ == "__main__":
    main()
