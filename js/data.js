// ChefMinistry — Signal Intelligence Data Layer
// ★ = Confirmed public data  |  ◎ = Illustrative / approximate for MVP

// ── Influencers ──────────────────────────────────────────────────────────────
const CM_INFLUENCERS = [

  // ── MEGA TIER (1M+ followers) ─────────────────────────────────────────────
  { id:"i01", name:"Peach Eat Laek",      handle:"@peach_eat_laek",    platform:"YouTube",   tier:"Mega",  followers:"8.8M",  focusArea:"All Thai Food, Eating Shows",      avatar:"P",  verified:true  }, // ★
  { id:"i02", name:"icesy168",            handle:"@icesy168",           platform:"TikTok",    tier:"Mega",  followers:"3.7M",  focusArea:"Mukbang, Eating Show",              avatar:"I",  verified:true  }, // ★
  { id:"i03", name:"พี่จ่า Peeja",        handle:"@peeja_pachim",       platform:"TikTok",    tier:"Mega",  followers:"2M",    focusArea:"Street Food, Local Thai",           avatar:"จ",  verified:true  }, // ★
  { id:"i04", name:"bewvaraporn",         handle:"@bewvaraporn",        platform:"TikTok",    tier:"Mega",  followers:"1.7M",  focusArea:"Food, Lifestyle",                   avatar:"B",  verified:true  }, // ★

  // ── MACRO TIER (100K–1M followers) ───────────────────────────────────────
  { id:"i05", name:"มหาชนี จุ๊บจิ๊บ",   handle:"@mahachaneejubjib",   platform:"Facebook",  tier:"Macro", followers:"800K",  focusArea:"Bangkok Restaurants, All",          avatar:"ม",  verified:true  }, // ★
  { id:"i06", name:"Mark Wiens",          handle:"@markwiens",          platform:"YouTube",   tier:"Mega",  followers:"8M",    focusArea:"Thai Street Food, Travel Food",      avatar:"M",  verified:true  }, // ★
  { id:"i07", name:"Qunfoh",             handle:"@qunfoh",             platform:"TikTok",    tier:"Macro", followers:"400K",  focusArea:"ASMR, Mukbang, Korean-Thai",         avatar:"Q",  verified:true  }, // ★
  { id:"i08", name:"GUN ASMR",           handle:"@gun_asmr",           platform:"TikTok",    tier:"Macro", followers:"250K",  focusArea:"ASMR Eating, Spicy Food",            avatar:"G",  verified:true  }, // ★
  { id:"i09", name:"Kodtap Moo",         handle:"@kodtap_moo",         platform:"TikTok",    tier:"Macro", followers:"130K",  focusArea:"Street Food, Grilled Pork",          avatar:"K",  verified:true  }, // ★
  { id:"i10", name:"Bon Bangkok",        handle:"@bon_bkk_food",       platform:"Instagram", tier:"Macro", followers:"170K",  focusArea:"Fine Dining, Bangkok Cafes",         avatar:"Bn", verified:false }, // ◎ Visa Wangsuphachart

  // ── MID TIER (10K–100K followers) ────────────────────────────────────────
  { id:"i11", name:"นุ่น Fine Dine",     handle:"@nun_finedine",       platform:"Instagram", tier:"Mid",   followers:"65K",   focusArea:"Fine Dining, Omakase, Japanese",    avatar:"น",  verified:false }, // ◎
  { id:"i12", name:"โต้ง Street BKK",   handle:"@tong_streetbkk",     platform:"TikTok",    tier:"Mid",   followers:"55K",   focusArea:"Street Food, Night Market",          avatar:"ต",  verified:false }, // ◎
  { id:"i13", name:"แนน Cafe Hunt",     handle:"@nan_cafehunt",       platform:"Instagram", tier:"Mid",   followers:"47K",   focusArea:"Cafe, Dessert, Brunch",              avatar:"น",  verified:false }, // ◎
  { id:"i14", name:"ตั้ม Budget Eats",  handle:"@tam_budgeteats",     platform:"TikTok",    tier:"Mid",   followers:"38K",   focusArea:"Budget Eats, Best Value",            avatar:"ต",  verified:false }, // ◎
  { id:"i15", name:"กอย Omakase BKK",  handle:"@koi_omakasebkk",     platform:"Instagram", tier:"Mid",   followers:"32K",   focusArea:"Omakase, Japanese, Wine Pairing",    avatar:"ก",  verified:false }, // ◎
  { id:"i16", name:"เฟิร์น Night Eats", handle:"@fern_nighteats",     platform:"TikTok",    tier:"Mid",   followers:"27K",   focusArea:"Night Market, Late Night Food",      avatar:"ฝ",  verified:false }, // ◎
  { id:"i17", name:"จอย Thai Regional", handle:"@joy_thairegional",   platform:"YouTube",   tier:"Mid",   followers:"20K",   focusArea:"Regional Thai, Traditional",          avatar:"จ",  verified:false }, // ◎
  { id:"i18", name:"กาย Michelin Watch",handle:"@gay_michelinwatch",  platform:"Instagram", tier:"Mid",   followers:"17K",   focusArea:"Michelin Star, Fine Dining",          avatar:"ก",  verified:false }, // ◎
  { id:"i19", name:"ดาว Eat Around",    handle:"@dao_eatround",       platform:"TikTok",    tier:"Mid",   followers:"14K",   focusArea:"Everyday Eats, Local Favorite",       avatar:"ด",  verified:false }, // ◎
  { id:"i20", name:"มุก Sweet Review",  handle:"@mook_sweetreview",   platform:"Instagram", tier:"Mid",   followers:"11K",   focusArea:"Dessert, Bakery, Sweets",             avatar:"ม",  verified:false }, // ◎
];

// ── Restaurants ──────────────────────────────────────────────────────────────
const CM_RESTAURANTS = [
  {
    id:"r001", name:"Gaggan Anand", cuisine:"Indian Progressive",
    type:"fine-dining", budget:3, budgetLabel:"฿฿฿",
    occasions:["special","date","business"], area:"วิทยุ",
    priceRange:"4,500–8,000", emoji:"🍛",
    signalStrength:"moderate",
    signalCount: 6,
    overlapSignal: 3,
    trendVelocity: "stable",
    trendBadge: "→ Stable",
    reviewerTiers: { mega:1, macro:2, mid:0 },
    recentReviewers: ["i01","i06","i04"],
    bookingLinks: { googlemaps:"#", wongnai:"#" },
    tags:["Michelin 2★","Tasting Menu","Reservation Required"],
    menuHighlights:["Yogurt Explosion","Potato Soil","Lick it up"],
    cmNote:"Mega Influencer 2 คนรีวิวภายใน 2 สัปดาห์ — Signal แข็งมาก ราคาสูงแต่ถูกพูดถึงในกลุ่ม Fine Dining เสมอ",
    totalReviews: 21
  },
  {
    id:"r002", name:"Le Du", cuisine:"Modern Thai Fine Dining",
    type:"fine-dining", budget:3, budgetLabel:"฿฿฿",
    occasions:["special","date","business"], area:"สีลม",
    priceRange:"2,500–4,000", emoji:"🌿",
    signalStrength:"very-strong", signalCount:9, overlapSignal:6,
    trendVelocity:"rising", trendBadge:"↑ Rising",
    reviewerTiers:{ mega:1, macro:3, mid:2 },
    recentReviewers:["i01","i08","i04","i06","i09","i07"],
    bookingLinks:{ googlemaps:"#", wongnai:"#" },
    tags:["Asia's 50 Best","Local Sourcing","Seasonal Menu"],
    menuHighlights:["Aged Duck","Thai Crab Curry","Local Herbs Dessert"],
    cmNote:"Signal ที่แข็งที่สุดในหมวด Fine Dining ไทย — Influencer หลาย tier พูดถึงพร้อมกัน นี่คือ Overlap Signal ที่ตรวจจับได้ชัด",
    totalReviews: 34
  },
  {
    id:"r003", name:"Jay Fai", cuisine:"Street Food Thai",
    type:"street-food", budget:2, budgetLabel:"฿฿",
    occasions:["casual","special"], area:"บางลำพู",
    priceRange:"800–1,500", emoji:"🦀",
    signalStrength:"strong", signalCount:12, overlapSignal:5,
    trendVelocity:"stable", trendBadge:"→ Stable",
    reviewerTiers:{ mega:2, macro:2, mid:1 },
    recentReviewers:["i01","i02","i04","i05","i10"],
    bookingLinks:{ googlemaps:"#" },
    tags:["Michelin 1★","Queue Required","Iconic"],
    menuHighlights:["Crab Omelette","Tom Yum Seafood","Dry Tom Yum"],
    cmNote:"Michelin + global fame ทำให้ signal สม่ำเสมอ แต่เป็น established name ทุกคนรู้จักอยู่แล้ว ไม่ใช่ร้านที่ต้องการ early signal",
    totalReviews: 72
  },
  {
    id:"r004", name:"ไก่ทอดโปโล", cuisine:"Thai Fried Chicken",
    type:"local", budget:1, budgetLabel:"฿",
    occasions:["casual","everyday"], area:"วิทยุ",
    priceRange:"150–300", emoji:"🍗",
    signalStrength:"strong", signalCount:10, overlapSignal:5,
    trendVelocity:"stable", trendBadge:"→ Stable",
    reviewerTiers:{ mega:1, macro:3, mid:1 },
    recentReviewers:["i02","i05","i03","i06","i01"],
    bookingLinks:{ googlemaps:"#" },
    tags:["Best Value","Local Legend","No Reservation"],
    menuHighlights:["ไก่ทอด","ข้าวมันไก่","น้ำจิ้มสูตรพิเศษ"],
    cmNote:"Local Legend ที่ดังมาหลายสิบปี — Signal สม่ำเสมอจาก Influencer หลาย tier แต่ไม่ใช่ emerging หรือ rising เป็นร้านที่ทุกคนรู้จักอยู่แล้ว ไม่มี exclusivity",
    totalReviews: 78
  },
  {
    id:"r005", name:"Sühring", cuisine:"Modern German Fine Dining",
    type:"fine-dining", budget:3, budgetLabel:"฿฿฿",
    occasions:["special","date","business"], area:"สาทร",
    priceRange:"5,000–9,000", emoji:"🥘",
    signalStrength:"moderate", signalCount:5, overlapSignal:3,
    trendVelocity:"stable", trendBadge:"→ Stable",
    reviewerTiers:{ mega:1, macro:1, mid:1 },
    recentReviewers:["i01","i06","i09"],
    bookingLinks:{ googlemaps:"#", wongnai:"#" },
    tags:["Asia's 50 Best","Twin Chefs","Tasting Menu"],
    menuHighlights:["Pork Knuckle Reimagined","Schnitzel Evolution","Black Forest"],
    cmNote:"Signal ที่ consistent มาก ทุกครั้งที่ influencer Fine Dining ไป คำตอบคือ positive ทำให้ Signal น่าเชื่อถือสูง",
    totalReviews: 19
  },
  {
    id:"r006", name:"Supanniga Eating Room", cuisine:"Thai Regional",
    type:"casual-dining", budget:2, budgetLabel:"฿฿",
    occasions:["casual","date","family"], area:"ทองหล่อ",
    priceRange:"400–700", emoji:"🍲",
    signalStrength:"moderate", signalCount:6, overlapSignal:3,
    trendVelocity:"stable", trendBadge:"→ Stable",
    reviewerTiers:{ mega:0, macro:2, mid:1 },
    recentReviewers:["i03","i07","i05"],
    bookingLinks:{ googlemaps:"#", wongnai:"#" },
    tags:["Regional Thai","Family Friendly","Good Ambiance"],
    menuHighlights:["ปลาทูต้มมะดัน","แกงป่าหมูชะมวง","ยำปลาดุกฟู"],
    cmNote:"Signal สม่ำเสมอจาก Macro-Mid tier influencer หมวด Casual Dining — ยังไม่มี Mega ให้ความสนใจ",
    totalReviews: 42
  },
  {
    id:"r007", name:"Somtum Der", cuisine:"Isaan Thai",
    type:"casual-dining", budget:2, budgetLabel:"฿฿",
    occasions:["casual","lunch"], area:"สีลม",
    priceRange:"300–500", emoji:"🌶️",
    signalStrength:"moderate", signalCount:8, overlapSignal:4,
    trendVelocity:"stable", trendBadge:"→ Stable",
    reviewerTiers:{ mega:0, macro:2, mid:2 },
    recentReviewers:["i10","i08","i05","i03"],
    bookingLinks:{ googlemaps:"#", wongnai:"#" },
    tags:["Michelin Bib Gourmand","Isaan Specialist","Great Value"],
    menuHighlights:["ส้มตำไทย","ลาบเป็ดคั่ว","ไก่ย่างตะกร้า"],
    cmNote:"Michelin Bib Gourmand ทำให้ Signal น่าเชื่อถือสูง Mega influencer ฝั่ง Street Food บางส่วนรีวิวด้วย",
    totalReviews: 55
  },
  {
    id:"r009", name:"Paste Bangkok", cuisine:"Modern Royal Thai",
    type:"fine-dining", budget:3, budgetLabel:"฿฿฿",
    occasions:["special","date","business"], area:"เพลินจิต",
    priceRange:"2,000–3,500", emoji:"👑",
    signalStrength:"moderate", signalCount:5, overlapSignal:3,
    trendVelocity:"stable", trendBadge:"→ Stable",
    reviewerTiers:{ mega:0, macro:1, mid:2 },
    recentReviewers:["i04","i06","i09"],
    bookingLinks:{ googlemaps:"#", wongnai:"#" },
    tags:["Michelin 1★","Royal Thai","Vegetarian Friendly"],
    menuHighlights:["Nahm Prik Roasted Chili","Royal Thai Curry","Blue Swimmer Crab"],
    cmNote:"Signal ที่ credible สูงจาก Fine Dining influencer — แม้จำนวนไม่มาก แต่ Tier สูง ทำให้ weight ของ Signal แข็ง",
    totalReviews: 24
  },
  {
    id:"r010", name:"Haoma", cuisine:"Neo-Indian Sustainable",
    type:"fine-dining", budget:3, budgetLabel:"฿฿฿",
    occasions:["special","date"], area:"สุขุมวิท",
    priceRange:"3,000–5,000", emoji:"🌱",
    signalStrength:"moderate", signalCount:5, overlapSignal:3,
    trendVelocity:"rising", trendBadge:"↑ Rising",
    reviewerTiers:{ mega:0, macro:1, mid:2 },
    recentReviewers:["i06","i03","i09"],
    bookingLinks:{ googlemaps:"#", wongnai:"#" },
    tags:["Sustainable","Asia's 50 Best","Aquaponic Garden"],
    menuHighlights:["Tasting Menu","Garden Fresh Produce","Neo-Indian Plates"],
    cmNote:"Emerging Signal ใน Niche Sustainability Food — Influencer เฉพาะกลุ่มกำลังสร้าง signal ที่ค่อยๆ แข็งขึ้น",
    totalReviews: 17
  },
  {
    id:"r011", name:"ข้าวมันไก่ประตูน้ำ", cuisine:"Thai Hainanese Chicken Rice",
    type:"street-food", budget:1, budgetLabel:"฿",
    occasions:["casual","everyday","lunch"], area:"ประตูน้ำ",
    priceRange:"60–100", emoji:"🍚",
    signalStrength:"strong", signalCount:10, overlapSignal:5,
    trendVelocity:"stable", trendBadge:"→ Stable",
    reviewerTiers:{ mega:1, macro:3, mid:1 },
    recentReviewers:["i02","i05","i01","i03","i06"],
    bookingLinks:{ googlemaps:"#" },
    tags:["Street Food Legend","Unbeatable Value","Local Icon"],
    menuHighlights:["ข้าวมันไก่ต้ม","ข้าวมันไก่ทอด","ซุปไก่"],
    cmNote:"Landmark ที่ทุกคนรู้จัก — Signal stable สม่ำเสมอ แต่ไม่มี surprise เหมือน Emerging Signal ไม่ใช่ประเภทที่ Pro user ต้องการข้อมูลล่วงหน้า",
    totalReviews: 88
  },
  {
    id:"r012", name:"Daniel Thaiger", cuisine:"Thai-American Street Food",
    type:"street-food", budget:1, budgetLabel:"฿",
    occasions:["casual","lunch","hangout"], area:"หลายสาขา",
    priceRange:"200–350", emoji:"🌮",
    signalStrength:"moderate", signalCount:5, overlapSignal:2,
    trendVelocity:"declining", trendBadge:"↓ Declining",
    reviewerTiers:{ mega:0, macro:1, mid:1 },
    recentReviewers:["i10","i08"],
    bookingLinks:{ googlemaps:"#" },
    tags:["Street Food","⚠️ Signal Declining","Multiple Locations"],
    menuHighlights:["Thai Burger","Sticky Rice Bowl","Pad Kra Pao Fries"],
    cmNote:"⚠️ Declining Signal — จำนวน influencer mention ลดลงจาก peak และเริ่มมี negative comment เรื่อง consistency หลังขยายสาขา Pro user ได้ข้อมูลนี้ก่อน",
    totalReviews: 38
  },
  {
    id:"r013", name:"Soul Food Thailand", cuisine:"Thai-Western Fusion",
    type:"casual-dining", budget:2, budgetLabel:"฿฿",
    occasions:["casual","date","hangout"], area:"เอกมัย",
    priceRange:"350–600", emoji:"🍹",
    signalStrength:"weak", signalCount:4, overlapSignal:2,
    trendVelocity:"stable", trendBadge:"→ Stable",
    reviewerTiers:{ mega:0, macro:1, mid:1 },
    recentReviewers:["i08","i03"],
    bookingLinks:{ googlemaps:"#", wongnai:"#" },
    tags:["Good Vibes","Craft Cocktails","Fusion"],
    menuHighlights:["Thai Tapas","Isaan Nachos","Craft Cocktails"],
    cmNote:"Signal มาจาก Lifestyle influencer เป็นหลัก — Mood/Vibe มากกว่า Food signal บอกว่าร้านนี้ถูกรีวิวเพราะ บรรยากาศ ไม่ใช่อาหาร",
    totalReviews: 28
  },
  {
    id:"r014", name:"Peppina", cuisine:"Neapolitan Pizza",
    type:"casual-dining", budget:2, budgetLabel:"฿฿",
    occasions:["casual","date","family"], area:"ทองหล่อ",
    priceRange:"400–700", emoji:"🍕",
    signalStrength:"moderate", signalCount:7, overlapSignal:4,
    trendVelocity:"stable", trendBadge:"→ Stable",
    reviewerTiers:{ mega:0, macro:2, mid:2 },
    recentReviewers:["i08","i03","i07","i05"],
    bookingLinks:{ googlemaps:"#", wongnai:"#" },
    tags:["Best Pizza BKK","Neapolitan DOC","Wood-fired Oven"],
    menuHighlights:["Margherita","Diavola","Burrata & Prosciutto"],
    cmNote:"Signal ที่สม่ำเสมอจาก Macro-Mid tier ในหมวด International Casual — บ่งบอกว่าคุณภาพ consistent และไม่มี controversy",
    totalReviews: 44
  },
  {
    id:"r015", name:"Eathai (Central Embassy)", cuisine:"Premium Thai Food Court",
    type:"food-court", budget:2, budgetLabel:"฿฿",
    occasions:["casual","lunch","family"], area:"เพลินจิต",
    priceRange:"200–450", emoji:"🏪",
    signalStrength:"moderate", signalCount:8, overlapSignal:4,
    trendVelocity:"stable", trendBadge:"→ Stable",
    reviewerTiers:{ mega:0, macro:2, mid:2 },
    recentReviewers:["i10","i08","i05","i03"],
    bookingLinks:{ googlemaps:"#" },
    tags:["Premium Food Court","Multiple Options","Great Location"],
    menuHighlights:["ก๋วยเตี๋ยวเรือ","Mango Sticky Rice","Southern Thai Curry"],
    cmNote:"Signal มาจาก Influencer หมวด Budget & Everyday — สะท้อนว่า Food Court คุณภาพสูงนี้เหมาะกับคนทุก segment",
    totalReviews: 52
  },
  // ── Farm-to-Table ─────────────────────────────────────────────────────────
  {
    id:"r019", name:"80/20 Bangkok", cuisine:"Farm-to-Table Progressive Thai",
    type:"fine-dining", budget:3, budgetLabel:"฿฿฿",
    occasions:["special","date","business"], area:"เจริญกรุง",
    priceRange:"2,800–4,500", emoji:"🌱",
    signalStrength:"strong", signalCount:9, overlapSignal:5,
    trendVelocity:"rising", trendBadge:"↑ Rising",
    reviewerTiers:{ mega:1, macro:2, mid:2 },
    recentReviewers:["i01","i05","i11","i06","i08"],
    bookingLinks:{ googlemaps:"#", wongnai:"#" },
    tags:["Farm-to-Table","Local Sourcing","Asia's 50 Best Watch"],
    menuHighlights:["100-Mile Menu","Fermented Local Ingredients","Seasonal Tasting"],
    cmNote:"กำลัง Rising อย่างน่าสนใจ — ร้าน Farm-to-Table ที่ใช้วัตถุดิบท้องถิ่น 100% Influencer Fine Dining เริ่ม mention มากขึ้นเรื่อยๆ",
    totalReviews: 31
  },
  {
    id:"r020", name:"Canvas Bangkok", cuisine:"Farm-to-Table Modern European",
    type:"fine-dining", budget:3, budgetLabel:"฿฿฿",
    occasions:["special","date"], area:"ทองหล่อ",
    priceRange:"3,200–5,500", emoji:"🎨",
    signalStrength:"moderate", signalCount:6, overlapSignal:3,
    trendVelocity:"rising", trendBadge:"↑ Rising",
    reviewerTiers:{ mega:0, macro:2, mid:2 },
    recentReviewers:["i11","i05","i15","i08"],
    bookingLinks:{ googlemaps:"#", wongnai:"#" },
    tags:["Farm-to-Table","Seasonal Menu","Natural Wine"],
    menuHighlights:["Daily-changing Tasting Menu","Organic Vegetables","House-made Bread"],
    cmNote:"Signal กำลัง build up — ร้านที่เน้น Seasonal Menu เปลี่ยนทุกวัน ทำให้ Influencer กลับมาซ้ำ สร้าง repeat signal ที่น่าสนใจ",
    totalReviews: 18
  },
  // ── Neapolitan Pizza ───────────────────────────────────────────────────────
  {
    id:"r025", name:"Maru Maru Pizza", cuisine:"Contemporary Neapolitan Pizza",
    type:"casual-dining", budget:2, budgetLabel:"฿฿",
    occasions:["casual","date","hangout"], area:"พระโขนง (สุขุมวิท 67)",
    priceRange:"380–750", emoji:"🍕",
    signalStrength:"strong", signalCount:8, overlapSignal:5,
    trendVelocity:"rising", trendBadge:"↑ Rising",
    reviewerTiers:{ mega:0, macro:3, mid:2 },
    recentReviewers:["i03","i08","i12","i07","i05"],
    bookingLinks:{ googlemaps:"#", wongnai:"#" },
    tags:["Viral TikTok","Reservation Required","Homemade Dough"],
    menuHighlights:["Burro Rosso","Smoked Belly","Vongole Pizza","Akira's Tiramisu"],
    cmNote:"🔥 Signal พุ่งแรงที่สุดใน Neapolitan Pizza — TikTok viral รอบใหม่ Macro Influencer หลายเจ้ารีวิวซ้ำ สัญญาณ Emerging → Established ที่ชัดเจน",
    totalReviews: 26
  },
  {
    id:"r021", name:"Pizza Massilia", cuisine:"Neapolitan Pizza",
    type:"casual-dining", budget:2, budgetLabel:"฿฿",
    occasions:["casual","date"], area:"สาทร",
    priceRange:"350–650", emoji:"🍕",
    signalStrength:"moderate", signalCount:5, overlapSignal:3,
    trendVelocity:"rising", trendBadge:"↑ Rising",
    reviewerTiers:{ mega:0, macro:2, mid:1 },
    recentReviewers:["i03","i08","i07"],
    bookingLinks:{ googlemaps:"#" },
    tags:["Neapolitan DOC","Thin Crust","AVPN Certified"],
    menuHighlights:["Margherita STG","Marinara","Calzone Classico"],
    cmNote:"Signal Rising ชัดเจน — เปิดใหม่ไม่นาน แต่ Macro Influencer หมวด Casual Dining เริ่ม mention ถี่ขึ้น สัญญาณ Emerging ที่ชัดเจน",
    totalReviews: 15
  },
  {
    id:"r022", name:"Motorino Bangkok", cuisine:"Neapolitan Pizza",
    type:"casual-dining", budget:2, budgetLabel:"฿฿",
    occasions:["casual","date","family"], area:"สุขุมวิท",
    priceRange:"320–600", emoji:"🛵",
    signalStrength:"moderate", signalCount:5, overlapSignal:2,
    trendVelocity:"stable", trendBadge:"→ Stable",
    reviewerTiers:{ mega:0, macro:1, mid:1 },
    recentReviewers:["i08","i07"],
    bookingLinks:{ googlemaps:"#", wongnai:"#" },
    tags:["Neapolitan","NY-Born Brand","Charred Crust"],
    menuHighlights:["Brussels Sprout Pizza","Speck & Truffle","Classic Marinara"],
    cmNote:"Signal stable จาก Macro-Mid tier — แบรนด์ที่มี following เดิม ไม่ explosive แต่ consistent signal ตลอดปี",
    totalReviews: 26
  },
  // ── Ramen (Rising Trend) ──────────────────────────────────────────────────
  {
    id:"r026", name:"Sendo Ramen", cuisine:"Modern Japanese Ramen",
    type:"casual-dining", budget:2, budgetLabel:"฿฿",
    occasions:["casual","lunch","date"], area:"สีลม (Thaniya Plaza)",
    priceRange:"280–480", emoji:"🍜",
    signalStrength:"moderate", signalCount:6, overlapSignal:4,
    trendVelocity:"rising", trendBadge:"↑ Rising",
    reviewerTiers:{ mega:0, macro:2, mid:2 },
    recentReviewers:["i09","i12","i07","i08"],
    bookingLinks:{ googlemaps:"#", wongnai:"#" },
    tags:["Thai-Japanese Fusion Ramen","Homemade Noodles","Craft Broth"],
    menuHighlights:["Shoyu Ramen","Tori Paitan","Thick Homemade Noodles"],
    cmNote:"กำลัง Rising ใน category Thai-led Ramen — ผลงานร่วมระหว่างเชฟ Shindo และผู้หลงใหลราเมน Influencer Casual Dining เริ่ม pick up signal ชัด",
    totalReviews: 19
  },
  {
    id:"r027", name:"Shindo Ramen", cuisine:"Artisan Japanese Ramen",
    type:"casual-dining", budget:2, budgetLabel:"฿฿",
    occasions:["casual","special"], area:"ศาลายา",
    priceRange:"250–420", emoji:"🍥",
    signalStrength:"moderate", signalCount:5, overlapSignal:3,
    trendVelocity:"rising", trendBadge:"↑ Rising",
    reviewerTiers:{ mega:0, macro:1, mid:2 },
    recentReviewers:["i09","i07","i17"],
    bookingLinks:{ googlemaps:"#" },
    tags:["Yokohama Ramen Museum Pop-up","Award-winning Broth","Worth the Journey"],
    menuHighlights:["Signature Tonkotsu","Tsukemen","Seasonal Limited Bowl"],
    cmNote:"ร้านราเมนไทยที่ได้รับเชิญไป pop-up ที่ Yokohama Ramen Museum ญี่ปุ่น — Signal authenticity สูงมาก Influencer สาย Ramen กระจาย mention",
    totalReviews: 13
  },
  // ── Steakhouse ────────────────────────────────────────────────────────────
  {
    id:"r023", name:"Wolfgang's Steakhouse Bangkok", cuisine:"American Steakhouse",
    type:"steakhouse", budget:3, budgetLabel:"฿฿฿",
    occasions:["special","business","date"], area:"สุขุมวิท",
    priceRange:"3,500–7,000", emoji:"🥩",
    signalStrength:"weak", signalCount:3, overlapSignal:2,
    trendVelocity:"declining", trendBadge:"↓ Declining",
    reviewerTiers:{ mega:0, macro:1, mid:1 },
    recentReviewers:["i04","i09"],
    bookingLinks:{ googlemaps:"#", wongnai:"#" },
    tags:["USDA Prime","28-day Dry-aged","NY Institution"],
    menuHighlights:["Porterhouse for Two","Wagyu Ribeye","NY Strip"],
    cmNote:"Signal Declining — Steakhouse โดยรวมกำลังถูก Omakase และ Fine Dining รูปแบบใหม่แย่งความสนใจ Influencer ลดการ mention ลงชัดเจน",
    totalReviews: 11
  },
  {
    id:"r024", name:"Opus Steak Bangkok", cuisine:"Modern Steakhouse",
    type:"steakhouse", budget:3, budgetLabel:"฿฿฿",
    occasions:["special","business"], area:"สีลม",
    priceRange:"2,800–5,500", emoji:"🔥",
    signalStrength:"weak", signalCount:3, overlapSignal:2,
    trendVelocity:"declining", trendBadge:"↓ Declining",
    reviewerTiers:{ mega:0, macro:1, mid:1 },
    recentReviewers:["i06","i18"],
    bookingLinks:{ googlemaps:"#", wongnai:"#" },
    tags:["Dry-aged","Wine-paired","Business Dining"],
    menuHighlights:["Australian Wagyu","Tomahawk","Bone Marrow Butter"],
    cmNote:"Signal อ่อน และ Declining — สะท้อน trend ใหญ่ที่ Steakhouse กำลังถูกแทนด้วย Omakase ใน segment Business Dining",
    totalReviews: 9
  },
  // ── Omakase ───────────────────────────────────────────────────────────────
  {
    id:"r016", name:"Sushi Masato", cuisine:"Japanese Omakase",
    type:"omakase", budget:3, budgetLabel:"฿฿฿",
    occasions:["special","date","business"], area:"สาทร",
    priceRange:"6,000–9,000", emoji:"🍣",
    signalStrength:"strong", signalCount:8, overlapSignal:5,
    trendVelocity:"rising", trendBadge:"↑ Rising",
    reviewerTiers:{ mega:1, macro:2, mid:2 },
    recentReviewers:["i01","i05","i11","i06","i04"],
    bookingLinks:{ googlemaps:"#", wongnai:"#" },
    tags:["Omakase","Reservation Required","World-Class Neta"],
    menuHighlights:["Omakase 20+ Courses","Premium Tuna","Uni & Wagyu"],
    cmNote:"Signal แข็งที่สุดในหมวด Omakase — Chef Masato เป็นที่รู้จักในวงการ Fine Dining ไทย Influencer หลาย tier รีวิวพร้อมกัน",
    totalReviews: 27
  },
  {
    id:"r017", name:"Sushi Ichizu", cuisine:"Japanese Omakase",
    type:"omakase", budget:3, budgetLabel:"฿฿฿",
    occasions:["special","date"], area:"ทองหล่อ",
    priceRange:"4,500–7,000", emoji:"🍱",
    signalStrength:"moderate", signalCount:6, overlapSignal:4,
    trendVelocity:"rising", trendBadge:"↑ Rising",
    reviewerTiers:{ mega:0, macro:2, mid:2 },
    recentReviewers:["i05","i11","i15","i07"],
    bookingLinks:{ googlemaps:"#", wongnai:"#" },
    tags:["Omakase","Edomae Style","Intimate 8 Seats"],
    menuHighlights:["Aged Bluefin Tuna","Hokkaido Uni","Seasonal Sashimi"],
    cmNote:"กำลัง Rising อย่างเงียบๆ — Macro Influencer เริ่ม mention มากขึ้น สัญญาณว่าจะเป็น next hot omakase ใน BKK",
    totalReviews: 15
  },
  {
    id:"r018", name:"Ginza Sushi Ichi", cuisine:"Japanese Omakase",
    type:"omakase", budget:3, budgetLabel:"฿฿฿",
    occasions:["special","business"], area:"เพลินจิต",
    priceRange:"5,500–8,500", emoji:"🔪",
    signalStrength:"moderate", signalCount:6, overlapSignal:3,
    trendVelocity:"stable", trendBadge:"→ Stable",
    reviewerTiers:{ mega:1, macro:1, mid:1 },
    recentReviewers:["i06","i11","i01"],
    bookingLinks:{ googlemaps:"#", wongnai:"#" },
    tags:["Michelin 1★ Tokyo","Premium Import","Counter Seating"],
    menuHighlights:["Omakase Nigiri","Seasonal Tsumami","Tamago Finale"],
    cmNote:"แบรนด์จาก Ginza Tokyo — Signal มาจาก Influencer ที่เน้น Fine Dining และ Japanese โดยเฉพาะ",
    totalReviews: 20
  },
  // ── Thai Fine Dining (Emerging Strongest) ────────────────────────────────
  {
    id:"r030", name:"Nusara", cuisine:"Modern Thai Fine Dining",
    type:"fine-dining", budget:3, budgetLabel:"฿฿฿",
    occasions:["special","date","business"], area:"สีลม",
    priceRange:"3,500–5,500", emoji:"🌺",
    signalStrength:"very-strong", signalCount:10, overlapSignal:7, // ◎
    trendVelocity:"rising", trendBadge:"↑ Rising",
    reviewerTiers:{ mega:1, macro:2, mid:4 },
    recentReviewers:["i01","i04","i06","i10","i11","i15","i18"],
    bookingLinks:{ googlemaps:"#", wongnai:"#" },
    tags:["Asia's 50 Best #5 (2026)","Michelin 1★","Rooftop View Wat Pho","Chefs' Choice Award 2026"],
    menuHighlights:["12-course Tasting Menu","Tiger Prawn Curry","River Fish","Seasonal Salads"],
    cmNote:"Signal แข็งที่สุดในหมวด Thai Fine Dining ตอนนี้ — Asia's 50 Best #5 ปี 2026 + Chef Ton ได้ Chefs' Choice Award Mega & Fine Dine influencer พูดถึงพร้อมกัน Overlap Signal Rising",
    totalReviews: 31
  },
  {
    id:"r031", name:"Baan Tepa", cuisine:"Thai Farm-to-Table",
    type:"fine-dining", budget:3, budgetLabel:"฿฿฿",
    occasions:["special","date"], area:"รามคำแหง",
    priceRange:"3,900–4,500", emoji:"🌿",
    signalStrength:"very-strong", signalCount:9, overlapSignal:6, // ◎
    trendVelocity:"rising", trendBadge:"↑ Rising",
    reviewerTiers:{ mega:1, macro:2, mid:3 },
    recentReviewers:["i01","i04","i06","i10","i11","i18"],
    bookingLinks:{ googlemaps:"#", wongnai:"#" },
    tags:["Asia's 50 Best #7 (2026)","Michelin 2★","Best Thai Restaurant 2026","Farm-to-Table","Garden Dining"],
    menuHighlights:["7-course Tasting Menu","Seasonal Thai Herbs","Garden Fresh Produce","Chef's Snack in Garden"],
    cmNote:"Best Thai Restaurant 2026 (Asia's 50 Best) — Chef Tam คนแรกในโลกที่เป็นผู้หญิงไทยนำร้าน Michelin 2 ดาว ตั้งอยู่ในบ้านเก่า 3 generation กำลังเป็น must-visit สำหรับ Fine Dine community",
    totalReviews: 24
  },
  {
    id:"r032", name:"ขวัญทิพย์ Kwantip", cuisine:"Samrub Thai Dining",
    type:"fine-dining", budget:3, budgetLabel:"฿฿฿",
    occasions:["special","date","family"], area:"อารีย์",
    priceRange:"1,390++", emoji:"👸",
    signalStrength:"moderate", signalCount:5, overlapSignal:3, // ◎
    trendVelocity:"rising", trendBadge:"↑ Rising",
    reviewerTiers:{ mega:0, macro:1, mid:2 },
    recentReviewers:["i05","i10","i11"],
    bookingLinks:{ googlemaps:"#", wongnai:"#" },
    tags:["Heritage Thai","Samrub Style","Reservation Required","Open Fri–Sun Only","4-Generation Recipe"],
    menuHighlights:["สำรับอาหารไทยตามฤดูกาล","น้ำพริกปลาสลิดฟู","ยำส้มโอเป็ดรมควัน","แกงปลา"],
    cmNote:"Emerging Signal ในหมวด Heritage Thai — เปิดเฉพาะ Fri–Sun โดยเชฟป้อม ม.ล.ขวัญทิพย์ เทวกุล สูตร 4 generation กำลังสร้าง buzz ในกลุ่ม Thai culture & fine dine community",
    totalReviews: 9
  },
  {
    id:"r033", name:"Sukiism", cuisine:"Chinese Hot Pot / Suki",
    type:"casual-dining", budget:2, budgetLabel:"฿฿",
    occasions:["casual","group","family"], area:"กรุงเทพฯ",
    priceRange:"300–600", emoji:"🍲",
    signalStrength:"moderate", signalCount:14, overlapSignal:4,
    trendVelocity:"stable", trendBadge:"→ Stable",
    reviewerTiers:{ mega:2, macro:3, mid:2 },
    recentReviewers:["i02","i03","i04","i07","i09","i12","i16"],
    bookingLinks:{ googlemaps:"#", wongnai:"#" },
    tags:["TikTok Viral","Hot Pot","Suki","Group Dining","Crowded Market"],
    menuHighlights:["น้ำซุปต้มยำ","สุกี้ทะเล","ชุดพรีเมียม"],
    cmNote:"Signal จาก TikTok volume สูง แต่ตลาด Hot Pot / Suki ใน กทม. อิ่มตัวมาก — มีคู่แข่งหลักร้อยร้าน Influencer รีวิวเพราะ format ทำง่าย ไม่ใช่เพราะร้านโดดเด่น",
    totalReviews: 28
  },
  {
    id:"r034", name:"Lok Toi Hot Pot", cuisine:"Chinese Hot Pot",
    type:"casual-dining", budget:2, budgetLabel:"฿฿",
    occasions:["casual","group","family"], area:"กรุงเทพฯ",
    priceRange:"350–700", emoji:"🥘",
    signalStrength:"moderate", signalCount:9, overlapSignal:3,
    trendVelocity:"stable", trendBadge:"→ Stable",
    reviewerTiers:{ mega:1, macro:2, mid:2 },
    recentReviewers:["i02","i07","i09","i12","i16"],
    bookingLinks:{ googlemaps:"#", wongnai:"#" },
    tags:["TikTok Trending","Hot Pot","Chinese","Group Dining","Crowded Market"],
    menuHighlights:["น้ำซุปหลากรส","เนื้อพรีเมียม","ชุดผัก"],
    cmNote:"อยู่ใน genre Hot Pot ที่ตลาด กทม. แน่นมาก — signal มาจาก TikTok format ไม่ใช่ความโดดเด่นของร้าน ควรดู Overlap ระยะยาวก่อนสรุป",
    totalReviews: 17
  },
  {
    id:"r035", name:"Ishii Katsu", cuisine:"Japanese Katsu",
    type:"casual-dining", budget:2, budgetLabel:"฿฿",
    occasions:["casual","date","solo"], area:"กรุงเทพฯ",
    priceRange:"350–700", emoji:"🍱",
    signalStrength:"strong", signalCount:7, overlapSignal:5,
    trendVelocity:"rising", trendBadge:"↑ Rising",
    reviewerTiers:{ mega:0, macro:2, mid:3 },
    recentReviewers:["i07","i09","i11","i15","i18"],
    bookingLinks:{ googlemaps:"#", wongnai:"#" },
    tags:["Hidden Gem","Japanese Katsu","Tonkatsu","ล้านลับ","Worth the Hunt"],
    menuHighlights:["Tonkatsu Premium","Hire Katsu","Katsu Curry"],
    cmNote:"Hidden Gem ที่ Influencer พูดถึงแบบ organic — ไม่ใช่ paid content ไม่ได้ดังจาก TikTok volume แต่ Overlap Signal แน่น นี่คือประเภท signal ที่ ChefMinistry ออกแบบมาเพื่อตรวจจับ",
    totalReviews: 14
  }
];

// ── Signal Intelligence for homepage ─────────────────────────────────────────
const CM_SIGNALS = {
  weeklyHighlight: {
    title: "🌟 ร้านอาหารที่มาแรงในสัปดาห์นี้!",
    desc: "Nusara และ Le Du ยังคงเป็นดาวเด่นในวงการอาหารไทย ขณะที่ Thai Fine Dining กำลังเติบโตอย่างรวดเร็ว!",
    trend: "rising"
  },
  trendCategories: [
    { cat:"Thai Fine Dining", signal:"very-strong", change:"+52%", influencers:8 },
    { cat:"Japanese Omakase", signal:"very-strong", change:"+34%", influencers:6 },
    { cat:"Hidden Gems",      signal:"strong",      change:"+40%", influencers:5 },
    { cat:"Neapolitan Pizza", signal:"strong",      change:"+22%", influencers:7 },
    { cat:"Artisan Ramen",    signal:"strong",      change:"+15%", influencers:5 },
    { cat:"Farm-to-Table",    signal:"rising",      change:"+18%", influencers:4 },
    { cat:"Thai Street Food", signal:"stable",      change:"+2%",  influencers:8 },
    { cat:"Hot Pot / Suki",   signal:"stable",      change:"Crowded", influencers:7 },
    { cat:"Steakhouse",       signal:"declining",   change:"-8%",  influencers:2 }
  ]
};

// ── Category meta ─────────────────────────────────────────────────────────────
const CM_CATEGORIES = [
  { id:"all",          label:"ทั้งหมด",      emoji:"🍽️" },
  { id:"fine-dining",  label:"Fine Dining",   emoji:"🥂" },
  { id:"omakase",      label:"Omakase",        emoji:"🍣" },
  { id:"casual-dining",label:"Casual Dining", emoji:"🍜" },
  { id:"ramen",        label:"Ramen",          emoji:"🍥" },
  { id:"street-food",  label:"Street Food",   emoji:"🌶️" },
  { id:"steakhouse",   label:"Steakhouse",     emoji:"🥩" },
  { id:"casual",       label:"Casual / Fast", emoji:"🍔" },
  { id:"local",        label:"Local Legend",  emoji:"⭐" },
  { id:"food-court",   label:"Food Court",    emoji:"🏪" }
];

// ── Helpers ───────────────────────────────────────────────────────────────────
function signalClass(s) {
  if (s === "very-strong") return "green";
  if (s === "strong")      return "green";
  if (s === "moderate")    return "amber";
  return "red";
}
function signalLabel(s) {
  if (s === "very-strong") return "Signal แข็งมาก";
  if (s === "strong")      return "Signal แข็ง";
  if (s === "moderate")    return "Signal ปานกลาง";
  return "Signal อ่อน";
}
function velocityClass(v) {
  return v === "rising" ? "green" : v === "declining" ? "red" : "amber";
}

function escHtml(v) {
  return String(v ?? "")
    .replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;")
    .replace(/"/g,"&quot;").replace(/'/g,"&#39;");
}
function getById(id) {
  return CM_RESTAURANTS.find(r => r.id === id);
}
function getInfluencerById(id) {
  return CM_INFLUENCERS.find(i => i.id === id);
}

function topByOverlap(n = 5) {
  return [...CM_RESTAURANTS].sort((a,b) => b.overlapSignal - a.overlapSignal).slice(0, n);
}
function topBySignalCount(n = 6) {
  return [...CM_RESTAURANTS].sort((a,b) => b.signalCount - a.signalCount).slice(0, n);
}
function getRising(n = 6) {
  return CM_RESTAURANTS.filter(r => r.trendVelocity === "rising").slice(0, n);
}
function getMostReviewed(n = 6) {
  return [...CM_RESTAURANTS].sort((a,b) => b.totalReviews - a.totalReviews).slice(0, n);
}

// ── Signal Badge ──────────────────────────────────────────────────────────────
function signalDots(overlapCount) {
  const max = 10;
  const filled = Math.min(overlapCount, max);
  return Array.from({length: max}, (_,i) =>
    `<span style="display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:2px;background:${i < filled ? "var(--green)" : "var(--border)"};"></span>`
  ).join("");
}

// ── Card Builder ──────────────────────────────────────────────────────────────
function buildRestaurantCard(r, opts = {}) {
  const sc = signalClass(r.signalStrength);
  const vc = velocityClass(r.trendVelocity);

  const trendHtml = `<div class="card-trend ${vc === "green" ? "trend-up" : vc === "red" ? "trend-down" : ""}">${r.trendBadge}</div>`;

  return `
    <div class="card restaurant-card">
      <a class="card-link" href="./restaurant.html?id=${escHtml(r.id)}">
        <div class="card-image">
          <div class="card-emoji-bg">${escHtml(r.emoji)}</div>
          ${trendHtml}
        </div>
        <div class="card-body">
          <div class="card-top">
            <div>
              <div class="card-name">${escHtml(r.name)}</div>
              <div class="card-cuisine">${escHtml(r.cuisine)} · ${escHtml(r.area)}</div>
            </div>
            <div class="signal-badge signal-${escHtml(r.signalStrength)}">${r.overlapSignal}<span style="font-size:10px;font-weight:700;margin-left:2px">INF</span></div>
          </div>
          <div class="card-insight">${escHtml(r.cmNote)}</div>
          <div class="overlap-bar" style="margin-top:4px">
            <div style="font-size:10px;font-weight:800;color:var(--text-2);text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px">Influencer Overlap</div>
            ${signalDots(r.overlapSignal)}
          </div>
          <div class="card-footer">
            <div class="tag-list">
              <span class="tag budget-${r.budget}">${escHtml(r.budgetLabel)}</span>
              <span class="signal-tag signal-${escHtml(r.signalStrength)}">${signalLabel(r.signalStrength)}</span>
            </div>
            <div class="card-area">📍 ${escHtml(r.area)}</div>
          </div>
        </div>
      </a>
    </div>`;
}

// -- DB Stats (injected by scraper) -------------------------------------------
const CM_DB_STATS = { total: 138, lastUpdated: "2026-04-06" };
