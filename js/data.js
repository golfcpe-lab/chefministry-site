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

  // ── YOUTUBE SOURCES ADDED ─────────────────────────────────────────────────
  { id:"i21", name:"Starvingtime",       handle:"@Starvingtime",       platform:"YouTube",   tier:"Mega",  followers:"2M+",   focusArea:"Thai Food, Street Food, Restaurant Reviews",  avatar:"St", verified:true  },
  { id:"i22", name:"Tid Review",         handle:"@tid_review",         platform:"YouTube",   tier:"Mega",  followers:"1M+",   focusArea:"Food Review, Thai & International",           avatar:"T",  verified:true  },
  { id:"i23", name:"EaterOat",           handle:"@EaterOat",           platform:"YouTube",   tier:"Macro", followers:"500K",  focusArea:"Food Review, Bangkok Restaurants",            avatar:"Eo", verified:true  },
  { id:"i24", name:"GoWentGo",           handle:"@GoWentGo",           platform:"YouTube",   tier:"Macro", followers:"350K",  focusArea:"Travel Food, Thai Restaurants, Hidden Gems",  avatar:"Gw", verified:true  },
  { id:"i25", name:"EatGuide",           handle:"@EatGuide",           platform:"YouTube",   tier:"Macro", followers:"280K",  focusArea:"Food Guide, Restaurant Reviews, All Thai",    avatar:"Eg", verified:true  },
  { id:"i26", name:"Kin Kub Ky",         handle:"@kin-kub-ky",         platform:"YouTube",   tier:"Macro", followers:"200K",  focusArea:"Thai Food, Everyday Eats, Local Favorite",   avatar:"K",  verified:true  },
  { id:"i27", name:"Henmuntookdee",      handle:"@Henmuntookdee",      platform:"YouTube",   tier:"Macro", followers:"150K",  focusArea:"Budget Eats, Best Value, Street Food",        avatar:"H",  verified:true  },
  { id:"i28", name:"KiaZaab",            handle:"@KiaZaab",            platform:"YouTube",   tier:"Mid",   followers:"80K",   focusArea:"Thai Street Food, Spicy, Local",              avatar:"Kz", verified:false },
  { id:"i29", name:"SauceChannel",       handle:"@SauceChannel",       platform:"YouTube",   tier:"Mid",   followers:"60K",   focusArea:"Sauces, Thai Cuisine, Cooking",               avatar:"Sc", verified:false },
  { id:"i30", name:"NanaEats",           handle:"@NanaEats",           platform:"YouTube",   tier:"Mid",   followers:"45K",   focusArea:"Everyday Eats, Local Food, Cafes",            avatar:"N",  verified:false },
  { id:"i31", name:"Harupiii",           handle:"@Harupiii",           platform:"YouTube",   tier:"Mid",   followers:"30K",   focusArea:"Cafe, Dessert, Japanese, Lifestyle",          avatar:"Hp", verified:false },
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
  },
  {
      id:"r036",
      name:"เนื้อตุ๋นสวนสยาม",
      cuisine:"Thai",
      type:"casual-dining",
      budget:1,
      budgetLabel:"฿",
      occasions:["casual", "date", "special", "business", "family"],
      area:"สวนสยาม",
      priceRange:"500–1,200",
      emoji:"🍲",
      signalStrength:"weak",
      signalCount:1,
      overlapSignal:1,
      trendVelocity:"rising",
      trendBadge:"↑ Rising",
      reviewerTiers:{mega:1, macro:0, mid:0},
      recentReviewers:["Peach Eat Laek"],
      bookingLinks:{googlemaps:"#", wongnai:"#"},
      tags:["เนื้อตุ๋น", "อาหารไทย"],
      menuHighlights:["เนื้อตุ๋นสูตรพิเศษ", "ข้าวสวยร้อนๆ", "น้ำจิ้มรสเด็ด"],
      cmNote:"ร้านนี้มีเนื้อตุ๋นที่นุ่มละมุนและรสชาติกลมกล่อมที่ไม่ควรพลาด!",
      totalReviews:1,
    },
  {
      id:"r037",
      name:"EATELIER",
      cuisine:"Chinese",
      type:"fine-dining",
      budget:2,
      budgetLabel:"฿฿",
      occasions:["casual", "date", "special", "business", "family"],
      area:"Siam Paragon, Bangkok",
      priceRange:"500–1,200",
      emoji:"🥢",
      signalStrength:"weak",
      signalCount:1,
      overlapSignal:1,
      trendVelocity:"rising",
      trendBadge:"↑ Rising",
      reviewerTiers:{mega:1, macro:0, mid:0},
      recentReviewers:["Peach Eat Laek"],
      bookingLinks:{googlemaps:"#", wongnai:"#"},
      tags:["Chinese", "fine-dining"],
      menuHighlights:["เมนู 1", "เมนู 2", "เมนู 3"],
      cmNote:"ร้านนี้มีเมนูจีนที่สร้างสรรค์และบรรยากาศที่น่าประทับใจ",
      totalReviews:1,
    },
  {
      id:"r038",
      name:"ข้าวแกงสวนลุม",
      cuisine:"Thai",
      type:"casual-dining",
      budget:1,
      budgetLabel:"฿",
      occasions:["casual", "date", "special", "business", "family"],
      area:"Bangkok",
      priceRange:"500–1,200",
      emoji:"🍛",
      signalStrength:"weak",
      signalCount:1,
      overlapSignal:1,
      trendVelocity:"rising",
      trendBadge:"↑ Rising",
      reviewerTiers:{mega:1, macro:0, mid:0},
      recentReviewers:["Peach Eat Laek"],
      bookingLinks:{googlemaps:"#", wongnai:"#"},
      tags:["ข้าวแกง", "อาหารไทย"],
      menuHighlights:["ข้าวแกงกะหรี่", "ผัดไทย", "ต้มยำกุ้ง"],
      cmNote:"ร้านนี้มีเมนูข้าวแกงที่หลากหลายและรสชาติอร่อย",
      totalReviews:1,
    },
  {
      id:"r039",
      name:"Qureshi Kebab",
      cuisine:"Indian",
      type:"casual-dining",
      budget:1,
      budgetLabel:"฿",
      occasions:["casual", "date", "special", "business", "family"],
      area:"Delhi",
      priceRange:"500–1,200",
      emoji:"🍢",
      signalStrength:"weak",
      signalCount:1,
      overlapSignal:1,
      trendVelocity:"rising",
      trendBadge:"↑ Rising",
      reviewerTiers:{mega:1, macro:0, mid:0},
      recentReviewers:["Mark Wiens"],
      bookingLinks:{googlemaps:"#", wongnai:"#"},
      tags:["kebab", "Indian food"],
      menuHighlights:["Seekh Kebab", "Tandoori Chicken", "Biryani"],
      cmNote:"ร้านนี้มีชื่อเสียงในเรื่องของเคบับที่อร่อยและบรรยากาศสบายๆ เหมาะสำหรับการนั่งทานกับครอบครัวหรือเพื่อนฝูง",
      totalReviews:1,
    },
  {
      id:"r040",
      name:"The Mak Trat",
      cuisine:"Seafood",
      type:"fine-dining",
      budget:1,
      budgetLabel:"฿฿",
      occasions:["casual", "date", "special", "business", "family"],
      area:"Koh Mak, Trat",
      priceRange:"500–1,200",
      emoji:"🦞",
      signalStrength:"weak",
      signalCount:1,
      overlapSignal:1,
      trendVelocity:"rising",
      trendBadge:"↑ Rising",
      reviewerTiers:{mega:0, macro:1, mid:0},
      recentReviewers:["GoWentGo"],
      bookingLinks:{googlemaps:"#", wongnai:"#"},
      tags:["seafood", "fine-dining"],
      menuHighlights:["เมนู 1", "เมนู 2", "เมนู 3"],
      cmNote:"ร้านนี้มีบรรยากาศที่ดีและอาหารทะเลสดใหม่ที่น่าสนใจ.",
      totalReviews:1,
    },
  {
      id:"r041",
      name:"เกาะหมากซีฟู้ด",
      cuisine:"Seafood",
      type:"casual-dining",
      budget:1,
      budgetLabel:"฿",
      occasions:["casual", "date", "special", "business", "family"],
      area:"Koh Mak, Trat",
      priceRange:"500–1,200",
      emoji:"🍤",
      signalStrength:"weak",
      signalCount:1,
      overlapSignal:1,
      trendVelocity:"rising",
      trendBadge:"↑ Rising",
      reviewerTiers:{mega:0, macro:1, mid:0},
      recentReviewers:["GoWentGo"],
      bookingLinks:{googlemaps:"#", wongnai:"#"},
      tags:["seafood", "beach"],
      menuHighlights:["ปูม้านึ่ง", "กุ้งเผา", "ปลากะพงทอด"],
      cmNote:"ร้านนี้มีบรรยากาศดีและอาหารทะเลสดใหม่ที่น่าลิ้มลอง.",
      totalReviews:1,
    },
  {
      id:"r042",
      name:"Cha Cha Beach Club",
      cuisine:"Thai",
      type:"casual-dining",
      budget:1,
      budgetLabel:"฿",
      occasions:["casual", "date", "special", "business", "family"],
      area:"Koh Mak, Trat",
      priceRange:"500–1,200",
      emoji:"🏖️",
      signalStrength:"weak",
      signalCount:1,
      overlapSignal:1,
      trendVelocity:"rising",
      trendBadge:"↑ Rising",
      reviewerTiers:{mega:0, macro:1, mid:0},
      recentReviewers:["GoWentGo"],
      bookingLinks:{googlemaps:"#", wongnai:"#"},
      tags:["beach", "Thai food"],
      menuHighlights:["ต้มยำกุ้ง", "ผัดไทย", "ส้มตำ"],
      cmNote:"ร้านนี้มีบรรยากาศริมทะเลที่น่าหลงใหลและอาหารไทยรสชาติเยี่ยม.",
      totalReviews:1,
    },
  {
      id:"r043",
      name:"Koh Mak Cococape Resort",
      cuisine:"Thai",
      type:"casual-dining",
      budget:1,
      budgetLabel:"฿",
      occasions:["casual", "date", "special", "business", "family"],
      area:"Koh Mak, Trat",
      priceRange:"500–1,200",
      emoji:"🏝️",
      signalStrength:"weak",
      signalCount:1,
      overlapSignal:1,
      trendVelocity:"rising",
      trendBadge:"↑ Rising",
      reviewerTiers:{mega:0, macro:1, mid:0},
      recentReviewers:["GoWentGo"],
      bookingLinks:{googlemaps:"#", wongnai:"#"},
      tags:["beachfront", "relaxing"],
      menuHighlights:["ต้มยำกุ้ง", "ผัดไทย", "แกงเขียวหวาน"],
      cmNote:"ร้านนี้มีบรรยากาศริมทะเลที่น่าหลงใหลและเมนูอาหารไทยที่อร่อยมาก.",
      totalReviews:1,
    },
  {
      id:"r044",
      name:"ครัวบ้านสีม่วง",
      cuisine:"Thai",
      type:"casual-dining",
      budget:1,
      budgetLabel:"฿",
      occasions:["casual", "date", "special", "business", "family"],
      area:"Koh Mak, Trat",
      priceRange:"500–1,200",
      emoji:"🍽️",
      signalStrength:"weak",
      signalCount:1,
      overlapSignal:1,
      trendVelocity:"rising",
      trendBadge:"↑ Rising",
      reviewerTiers:{mega:0, macro:1, mid:0},
      recentReviewers:["GoWentGo"],
      bookingLinks:{googlemaps:"#", wongnai:"#"},
      tags:["local", "family-friendly"],
      menuHighlights:["เมนู 1", "เมนู 2", "เมนู 3"],
      cmNote:"ร้านนี้มีบรรยากาศอบอุ่นและเหมาะสำหรับครอบครัว.",
      totalReviews:1,
    },
  {
      id:"r045",
      name:"เก๋ามังกร",
      cuisine:"Thai",
      type:"fine-dining",
      budget:2,
      budgetLabel:"฿฿",
      occasions:["casual", "date", "special", "business", "family"],
      area:"Bangna",
      priceRange:"500–1,200",
      emoji:"🍜",
      signalStrength:"weak",
      signalCount:1,
      overlapSignal:1,
      trendVelocity:"rising",
      trendBadge:"↑ Rising",
      reviewerTiers:{mega:0, macro:0, mid:1},
      recentReviewers:["KiaZaab"],
      bookingLinks:{googlemaps:"#", wongnai:"#"},
      tags:["Thai cuisine", "Bangna"],
      menuHighlights:["ต้มยำกุ้ง", "ผัดไทย", "แกงเขียวหวาน"],
      cmNote:"ร้านนี้มีเมนูไทยที่หลากหลายและรสชาติเข้มข้น น่าสนใจมากสำหรับคนรักอาหารไทย.",
      totalReviews:1,
    },
  {
      id:"r046",
      name:"ข้าวหมูทอง",
      cuisine:"Thai",
      type:"casual-dining",
      budget:1,
      budgetLabel:"฿",
      occasions:["casual", "date", "special", "business", "family"],
      area:"ศรีนครินทร์",
      priceRange:"500–1,200",
      emoji:"🍚",
      signalStrength:"weak",
      signalCount:1,
      overlapSignal:1,
      trendVelocity:"rising",
      trendBadge:"↑ Rising",
      reviewerTiers:{mega:0, macro:0, mid:1},
      recentReviewers:["EatGuide"],
      bookingLinks:{googlemaps:"#", wongnai:"#"},
      tags:["ข้าวหมู", "อาหารไทย"],
      menuHighlights:["ข้าวหมูทอดกรอบ", "ต้มยำกุ้ง", "ผัดไทย"],
      cmNote:"ร้านนี้มีเมนูข้าวหมูที่อร่อยและบรรยากาศสบายๆ เหมาะสำหรับการนั่งทานกับครอบครัวหรือเพื่อนฝูง.",
      totalReviews:1,
    },
  {
      id:"r047",
      name:"ซูชิมิโดริ",
      cuisine:"Japanese",
      type:"fine-dining",
      budget:2,
      budgetLabel:"฿฿",
      occasions:["casual", "date", "special", "business", "family"],
      area:"Bangkok",
      priceRange:"500–1,200",
      emoji:"🍣",
      signalStrength:"weak",
      signalCount:1,
      overlapSignal:1,
      trendVelocity:"rising",
      trendBadge:"↑ Rising",
      reviewerTiers:{mega:0, macro:0, mid:1},
      recentReviewers:["EatGuide"],
      bookingLinks:{googlemaps:"#", wongnai:"#"},
      tags:["sushi", "Japanese"],
      menuHighlights:["ซูชิปลาแซลมอน", "ซาชิมิ", "ข้าวปั้น"],
      cmNote:"ร้านซูชิมิโดริมีเมนูซูชิสดใหม่และบรรยากาศที่น่านั่ง.",
      totalReviews:1,
    },
  {
      id:"r048",
      name:"mini oriental",
      cuisine:"Thai",
      type:"casual-dining",
      budget:1,
      budgetLabel:"฿",
      occasions:["casual", "date", "special", "business", "family"],
      area:"Bangkok",
      priceRange:"500–1,200",
      emoji:"🍜",
      signalStrength:"weak",
      signalCount:1,
      overlapSignal:1,
      trendVelocity:"rising",
      trendBadge:"↑ Rising",
      reviewerTiers:{mega:0, macro:0, mid:1},
      recentReviewers:["EatGuide"],
      bookingLinks:{googlemaps:"#", wongnai:"#"},
      tags:["Thai", "casual"],
      menuHighlights:["ต้มยำกุ้ง", "ผัดไทย", "แกงเขียวหวาน"],
      cmNote:"ร้านนี้มีเมนูไทยที่หลากหลายและบรรยากาศที่น่านั่ง.",
      totalReviews:1,
    },
  {
      id:"r049",
      name:"ห้องอาหารกิ๊ดกี่",
      cuisine:"Thai",
      type:"fine-dining",
      budget:2,
      budgetLabel:"฿฿",
      occasions:["casual", "date", "special", "business", "family"],
      area:"สำเหร่",
      priceRange:"500–1,200",
      emoji:"🍽️",
      signalStrength:"weak",
      signalCount:1,
      overlapSignal:1,
      trendVelocity:"rising",
      trendBadge:"↑ Rising",
      reviewerTiers:{mega:0, macro:0, mid:1},
      recentReviewers:["EatGuide"],
      bookingLinks:{googlemaps:"#", wongnai:"#"},
      tags:["Thai cuisine", "fine dining"],
      menuHighlights:["ต้มยำกุ้ง", "ผัดไทย", "แกงเขียวหวาน"],
      cmNote:"ร้านนี้มีเมนูไทยที่หลากหลายและบรรยากาศดีเหมาะสำหรับทุกโอกาส",
      totalReviews:1,
    },
  {
      id:"r050",
      name:"หมาล่าไม้หมุน",
      cuisine:"Chinese",
      type:"casual-dining",
      budget:1,
      budgetLabel:"฿",
      occasions:["casual", "date", "special", "business", "family"],
      area:"Bangkok",
      priceRange:"500–1,200",
      emoji:"🍜",
      signalStrength:"weak",
      signalCount:1,
      overlapSignal:1,
      trendVelocity:"rising",
      trendBadge:"↑ Rising",
      reviewerTiers:{mega:1, macro:0, mid:0},
      recentReviewers:["Peach Eat Laek"],
      bookingLinks:{googlemaps:"#", wongnai:"#"},
      tags:["Chinese", "Street Food"],
      menuHighlights:["หมาล่า", "ข้าวผัด", "ซุปเสฉวน"],
      cmNote:"ร้านนี้มีเมนูหมาล่าที่อร่อยและบรรยากาศสบายๆ เหมาะสำหรับการนัดพบเพื่อน.",
      totalReviews:1,
    },
  {
      id:"r051",
      name:"เนื้อฉ่ำ",
      cuisine:"Thai",
      type:"steakhouse",
      budget:2,
      budgetLabel:"฿฿",
      occasions:["casual", "date", "special", "business", "family"],
      area:"สุขุมวิท",
      priceRange:"500–1,200",
      emoji:"🥩",
      signalStrength:"weak",
      signalCount:1,
      overlapSignal:1,
      trendVelocity:"rising",
      trendBadge:"↑ Rising",
      reviewerTiers:{mega:0, macro:0, mid:1},
      recentReviewers:["EatGuide"],
      bookingLinks:{googlemaps:"#", wongnai:"#"},
      tags:["steak", "Thai cuisine"],
      menuHighlights:["เนื้อย่าง", "สเต๊กซอสพริกไทย", "สลัดผักสด"],
      cmNote:"ร้านนี้มีเนื้อคุณภาพเยี่ยมและบรรยากาศที่เหมาะสำหรับการสังสรรค์.",
      totalReviews:1,
    },
];

// ── Signal Intelligence for homepage ─────────────────────────────────────────
const CM_SIGNALS = {
  weeklyHighlight: {
    title: "🌟 สัปดาห์นี้! ร้านดังมาแรงที่ไม่ควรพลาด",
    desc: "ร้านเนื้อตุ๋นสวนสยามยังคงได้รับความนิยมสูง แต่มีร้านใหม่ๆ อย่างหมาล่าไม้หมุนและครัวบ้านสีม่วงที่น่าสนใจไม่แพ้กัน!",
    restaurant: "หมาล่าไม้หมุน",
    trend: "rising"
  },
  trendCategories: [
    { cat:"Thai Fine Dining", signal:"strong", change:"+32%", influencers:4 },
    { cat:"Japanese Omakase", signal:"stable", change:"+8%", influencers:1 },
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
            <div class="signal-badge signal-${escHtml(r.signalStrength)}">${r.totalReviews||0}<span style="font-size:10px;font-weight:700;margin-left:2px">รีวิว</span></div>
          </div>
          <div class="card-insight">${escHtml(r.cmNote)}</div>
          <div class="overlap-bar" style="margin-top:4px">
            <div style="font-size:10px;font-weight:800;color:var(--text-2);text-transform:uppercase;letter-spacing:.06em;margin-bottom:4px">Creator Signal <span style="font-weight:400;opacity:.6">(ข้อมูลเสริม)</span></div>
            ${signalDots(r.overlapSignal)}
          </div>
          <div class="card-footer">
            <div class="tag-list">
              <span class="tag budget-${r.budget}">${escHtml(r.budgetLabel)}</span>
              <span class="velocity ${escHtml(r.trendVelocity)}">${escHtml(r.trendBadge)}</span>
              <span class="signal-tag signal-${escHtml(r.signalStrength)}" style="font-size:9px;opacity:.75">${signalLabel(r.signalStrength)}</span>
            </div>
            <div class="card-area">📍 ${escHtml(r.area)}</div>
          </div>
        </div>
      </a>
    </div>`;
}

// -- DB Stats (injected by scraper) -------------------------------------------
const CM_DB_STATS = { total: 138, lastUpdated: "2026-04-09" };
const CM_EXTERNAL_RESTAURANTS = [{"id": "wongnai_20696", "name": "เจ๊เบิ๊บโภชนา", "cuisine": "Street-Food", "area": "Silom", "type": "street-food", "budget": 1, "budgetLabel": "฿", "signalStrength": "strong", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "rising", "trendBadge": "↑ Rising Fast", "totalReviews": 52, "newReviews30d": 15, "velocityPct": 40.5, "tags": ["street-food", "silom", "wongnai"], "cmNote": "🔥 Review เพิ่ม +40% ใน 30 วัน — น่าจับตา", "isRestaurant": false, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/20696xR-%E0%B9%80%E0%B8%88%E0%B9%8A%E0%B9%80%E0%B8%9A%E0%B8%B4%E0%B9%8A%E0%B8%9A%E0%B9%82%E0%B8%A0%E0%B8%8A%E0%B8%99%E0%B8%B2", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_207727", "name": "เผือกทอดศาลาแดงซอย๑", "cuisine": "Street-Food", "area": "Silom", "type": "street-food", "budget": 1, "budgetLabel": "฿", "signalStrength": "moderate", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "rising", "trendBadge": "↑ Rising", "totalReviews": 11, "newReviews30d": 1, "velocityPct": 10.0, "tags": ["street-food", "silom", "wongnai"], "cmNote": "↑ Traffic กำลังเพิ่มบน Wongnai", "isRestaurant": false, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/207727qE-%E0%B9%80%E0%B8%9C%E0%B8%B7%E0%B8%AD%E0%B8%81%E0%B8%97%E0%B8%AD%E0%B8%94%E0%B8%A8%E0%B8%B2%E0%B8%A5%E0%B8%B2%E0%B9%81%E0%B8%94%E0%B8%87%E0%B8%8B%E0%B8%AD%E0%B8%A2%E0%B9%91", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_chefman", "name": "sathorn", "cuisine": "Other", "area": "Sathorn", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "stable", "trendBadge": "→ Stable", "totalReviews": 0, "newReviews30d": 0, "velocityPct": 0, "tags": ["other", "sathorn", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/chefman-sathorn?_st=cD01O2I9MTI4Mjk2O2FkPWZhbHNlO3Q9MTc3NTM3OTU2NDcwNztyaT0xWDdiVnRHYVRkSWdWODhrQnc5aFh0ZnJQdlRROVA7aT0xWDcwekQyQXpPeHJGcTM2WlVZT2p3SGloS01YUG47d3JlZj1zcjs%3D", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_1726468HQ", "name": "aaa", "cuisine": "Other", "area": "On Nut", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -1, "velocityPct": -100.0, "tags": ["other", "onnut", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/1726468HQ-aaa?_st=cD03O2I9MTcyNjQ2ODthZD1mYWxzZTt0PTE3NzUzNzk1NzE4Mjk7cmk9MVg3YlZ0R2JKaUxOMVFvaVVTNHJnWU91Qkk5cGx1O2k9MVg3MHpEMkJ1WGxRcEpXMXJhQko1VkVLdUJ4MWoyO3dyZWY9c3I7", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_139478", "name": "ยำแหนมคอนแวนต์", "cuisine": "Street-Food", "area": "Silom", "type": "street-food", "budget": 1, "budgetLabel": "฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 13, "newReviews30d": -2, "velocityPct": -13.3, "tags": ["street-food", "silom", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": false, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/139478BK-%E0%B8%A2%E0%B8%B3%E0%B9%81%E0%B8%AB%E0%B8%99%E0%B8%A1%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%81%E0%B8%A7%E0%B8%99%E0%B8%95%E0%B9%8C", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_2663029", "name": "หมูปิ้งมหานคร ศาลาแดง", "cuisine": "Street-Food", "area": "Silom", "type": "street-food", "budget": 1, "budgetLabel": "฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 8, "newReviews30d": -3, "velocityPct": -27.3, "tags": ["street-food", "silom", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": false, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/listings/foods-around-silom-district#2663029", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_268864", "name": "สุกี้บางรัก", "cuisine": "Street-Food", "area": "Silom", "type": "street-food", "budget": 1, "budgetLabel": "฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 7, "newReviews30d": -5, "velocityPct": -41.7, "tags": ["street-food", "silom", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": false, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/268864Mt-%E0%B8%AA%E0%B8%B8%E0%B8%81%E0%B8%B5%E0%B9%89%E0%B8%9A%E0%B8%B2%E0%B8%87%E0%B8%A3%E0%B8%B1%E0%B8%81", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_1742664AU", "name": "curry on สาทร 11", "cuisine": "Other", "area": "Sathorn", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -6, "velocityPct": -100.0, "tags": ["other", "sathorn", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/1742664AU-curry-on-%E0%B8%AA%E0%B8%B2%E0%B8%97%E0%B8%A3-11", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_2426", "name": "บ่อกุ้ง รัชดา-ท่าพระซอย 8 ฝั่งธน", "cuisine": "Thai", "area": "Ratchada", "type": "thai", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 54, "newReviews30d": -8, "velocityPct": -12.9, "tags": ["thai", "ratchada", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/2426Vz-%E0%B8%9A%E0%B9%88%E0%B8%AD%E0%B8%81%E0%B8%B8%E0%B9%89%E0%B8%87-%E0%B8%A3%E0%B8%B1%E0%B8%8A%E0%B8%94%E0%B8%B2-%E0%B8%97%E0%B9%88%E0%B8%B2%E0%B8%9E%E0%B8%A3%E0%B8%B0%E0%B8%8B%E0%B8%AD%E0%B8%A2-8-%E0%B8%9D%E0%B8%B1%E0%B9%88%E0%B8%87%E0%B8%98%E0%B8%99", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_2395023xk", "name": "starbucks rajanakarn building", "cuisine": "Other", "area": "Sathorn", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -8, "velocityPct": -100.0, "tags": ["other", "sathorn", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/2395023xk-starbucks-rajanakarn-building?_st=cD0yO2I9MjM5NTAyMzthZD1mYWxzZTt0PTE3NzUzNzk1NjQ2OTY7cmk9MVg3YlZ0R2FRNGR1ZFpzVkxMT0drb1ZQMjA4MzF6O2k9MVg3MHpEMkF6T3hyRnEzNlpVWU9qd0hpaEtNWFBuO3dyZWY9c3I7", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_771057LV", "name": "intchon อินชอนไก่ทอดนานาชาติ สาทร 11", "cuisine": "Other", "area": "Sathorn", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -12, "velocityPct": -100.0, "tags": ["other", "sathorn", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/771057LV-intchon-%E0%B8%AD%E0%B8%B4%E0%B8%99%E0%B8%8A%E0%B8%AD%E0%B8%99%E0%B9%84%E0%B8%81%E0%B9%88%E0%B8%97%E0%B8%AD%E0%B8%94%E0%B8%99%E0%B8%B2%E0%B8%99%E0%B8%B2%E0%B8%8A%E0%B8%B2%E0%B8%95%E0%B8%B4-%E0%B8%AA%E0%B8%B2%E0%B8%97%E0%B8%A3-11", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_280005", "name": "ก้อง บะหมี่กวางตุ้ง", "cuisine": "Street-Food", "area": "Silom", "type": "street-food", "budget": 1, "budgetLabel": "฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 14, "newReviews30d": -13, "velocityPct": -48.1, "tags": ["street-food", "silom", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": false, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/listings/foods-around-silom-district#280005", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_266972", "name": "กะเพราผัด รัชบาร์", "cuisine": "Other", "area": "Ratchada", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 17, "newReviews30d": -19, "velocityPct": -52.8, "tags": ["other", "ratchada", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/266972mF-%E0%B8%81%E0%B8%B0%E0%B9%80%E0%B8%9E%E0%B8%A3%E0%B8%B2%E0%B8%9C%E0%B8%B1%E0%B8%94-%E0%B8%A3%E0%B8%B1%E0%B8%8A%E0%B8%9A%E0%B8%B2%E0%B8%A3%E0%B9%8C", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_2291080hw", "name": "baimiang healthy shop ใบเมี่ยง empire tower", "cuisine": "Other", "area": "Sathorn", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -25, "velocityPct": -100.0, "tags": ["other", "sathorn", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/2291080hw-baimiang-healthy-shop-%E0%B9%83%E0%B8%9A%E0%B9%80%E0%B8%A1%E0%B8%B5%E0%B9%88%E0%B8%A2%E0%B8%87-empire-tower?_st=cD00O2I9MjI5MTA4MDthZD1mYWxzZTt0PTE3NzUzNzk1NjQ3MDc7cmk9MVg3YlZ0R2FSQ1VFTXdiZGZadFViRjRUbU9XeUJtO2k9MVg3MHpEMkF6T3hyRnEzNlpVWU9qd0hpaEtNWFBuO3dyZWY9c3I7", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_358776iF", "name": "คลั่ง อาหารป่า ปลาแม่น้ำ พุทธมณฑล สาย2 ได้รับมาตรฐาน sha", "cuisine": "Other", "area": "On Nut", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -29, "velocityPct": -100.0, "tags": ["other", "onnut", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/358776iF-%E0%B8%84%E0%B8%A5%E0%B8%B1%E0%B9%88%E0%B8%87-%E0%B8%AD%E0%B8%B2%E0%B8%AB%E0%B8%B2%E0%B8%A3%E0%B8%9B%E0%B9%88%E0%B8%B2-%E0%B8%9B%E0%B8%A5%E0%B8%B2%E0%B9%81%E0%B8%A1%E0%B9%88%E0%B8%99%E0%B9%89%E0%B8%B3-%E0%B8%9E%E0%B8%B8%E0%B8%97%E0%B8%98%E0%B8%A1%E0%B8%93%E0%B8%91%E0%B8%A5-%E0%B8%AA%E0%B8%B2%E0%B8%A22-%E0%B9%84%E0%B8%94%E0%B9%89%E0%B8%A3%E0%B8%B1%E0%B8%9A%E0%B8%A1%E0%B8%B2%E0%B8%95%E0%B8%A3%E0%B8%90%E0%B8%B2%E0%B8%99-sha?_st=cD0zO2I9MzU4Nzc2O2FkPWZhbHNlO3Q9MTc3NTM3OTU3MTgyNjtyaT0xWDdiVnRHYk1aemhacnNFRXl2bjVFejVoN3dmQlo7aT0xWDcwekQyQnVYbFFwSlcxcmFCSjVWRUt1QngxajI7d3JlZj1zcjs%3D", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_22744", "name": "ก๋วยเตี๋ยวเป็ด ซอยคอนแวนต์", "cuisine": "Street-Food", "area": "Silom", "type": "street-food", "budget": 1, "budgetLabel": "฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 15, "newReviews30d": -30, "velocityPct": -66.7, "tags": ["street-food", "silom", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": false, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/22744sB-%E0%B8%81%E0%B9%8B%E0%B8%A7%E0%B8%A2%E0%B9%80%E0%B8%95%E0%B8%B5%E0%B9%8B%E0%B8%A2%E0%B8%A7%E0%B9%80%E0%B8%9B%E0%B9%87%E0%B8%94-%E0%B8%8B%E0%B8%AD%E0%B8%A2%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%81%E0%B8%A7%E0%B8%99%E0%B8%95%E0%B9%8C", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_2592388", "name": "โรตีใบเตย ศาลาแดง", "cuisine": "Street-Food", "area": "Silom", "type": "street-food", "budget": 1, "budgetLabel": "฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 3, "newReviews30d": -35, "velocityPct": -92.1, "tags": ["street-food", "silom", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": false, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/listings/foods-around-silom-district#2592388", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_60368", "name": "ก๋วยเตี๋ยวหลอดเจ๊ใหญ่ (บางรัก)", "cuisine": "Street-Food", "area": "Silom", "type": "street-food", "budget": 1, "budgetLabel": "฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 27, "newReviews30d": -38, "velocityPct": -58.5, "tags": ["street-food", "silom", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": false, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/60368zj-%E0%B8%81%E0%B9%8B%E0%B8%A7%E0%B8%A2%E0%B9%80%E0%B8%95%E0%B8%B5%E0%B9%8B%E0%B8%A2%E0%B8%A7%E0%B8%AB%E0%B8%A5%E0%B8%AD%E0%B8%94%E0%B9%80%E0%B8%88%E0%B9%8A%E0%B9%83%E0%B8%AB%E0%B8%8D%E0%B9%88-%E0%B8%9A%E0%B8%B2%E0%B8%87%E0%B8%A3%E0%B8%B1%E0%B8%81", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_340314", "name": "Ramen Ippudo Central Rama 9", "cuisine": "Japanese", "area": "Rama 9", "type": "japanese", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 183, "newReviews30d": -42, "velocityPct": -18.7, "tags": ["japanese", "rama9", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/340314Pv-ramen-ippudo-central-rama-9", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_950488GK", "name": "baimiang healthy shop ใบเมี่ยง ลาวิลล่าอารีย์", "cuisine": "Other", "area": "Ari", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -43, "velocityPct": -100.0, "tags": ["other", "ari", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/950488GK-baimiang-healthy-shop-%E0%B9%83%E0%B8%9A%E0%B9%80%E0%B8%A1%E0%B8%B5%E0%B9%88%E0%B8%A2%E0%B8%87-%E0%B8%A5%E0%B8%B2%E0%B8%A7%E0%B8%B4%E0%B8%A5%E0%B8%A5%E0%B9%88%E0%B8%B2%E0%B8%AD%E0%B8%B2%E0%B8%A3%E0%B8%B5%E0%B8%A2%E0%B9%8C", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_189984", "name": "ข้าวมันไก่ตอน นายน้อยเจ้าเก่า ถนนคอนแวน", "cuisine": "Street-Food", "area": "Silom", "type": "street-food", "budget": 1, "budgetLabel": "฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 8, "newReviews30d": -57, "velocityPct": -87.7, "tags": ["street-food", "silom", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": false, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/189984sb-%E0%B8%82%E0%B9%89%E0%B8%B2%E0%B8%A7%E0%B8%A1%E0%B8%B1%E0%B8%99%E0%B9%84%E0%B8%81%E0%B9%88%E0%B8%95%E0%B8%AD%E0%B8%99-%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B8%99%E0%B9%89%E0%B8%AD%E0%B8%A2%E0%B9%80%E0%B8%88%E0%B9%89%E0%B8%B2%E0%B9%80%E0%B8%81%E0%B9%88%E0%B8%B2-%E0%B8%96%E0%B8%99%E0%B8%99%E0%B8%84%E0%B8%AD%E0%B8%99%E0%B9%81%E0%B8%A7%E0%B8%99", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_63891", "name": "เจ๊ติ๋มซีฟู้ด", "cuisine": "Thai", "area": "Ratchada", "type": "thai", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 18, "newReviews30d": -63, "velocityPct": -77.8, "tags": ["thai", "ratchada", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/63891FP-%E0%B9%80%E0%B8%88%E0%B9%8A%E0%B8%95%E0%B8%B4%E0%B9%8B%E0%B8%A1%E0%B8%8B%E0%B8%B5%E0%B8%9F%E0%B8%B9%E0%B9%89%E0%B8%94", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_2795187ia", "name": "uncle yod pork leg", "cuisine": "Other", "area": "On Nut", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -78, "velocityPct": -100.0, "tags": ["other", "onnut", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/2795187ia-uncle-yod-pork-leg?_st=cD05O2I9Mjc5NTE4NzthZD1mYWxzZTt0PTE3NzUzNzk1NzE4Mjk7cmk9MVg3YlZ0R2JNRHBkOGh2eE54MEZ2a1hsODhXZU1GO2k9MVg3MHpEMkJ1WGxRcEpXMXJhQko1VkVLdUJ4MWoyO3dyZWY9c3I7", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_270", "name": "แซ่บวัน ตำซั่ว Original", "cuisine": "Isaan", "area": "Ratchada", "type": "isaan", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 313, "newReviews30d": -79, "velocityPct": -20.2, "tags": ["isaan", "ratchada", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/270Rq-%E0%B9%81%E0%B8%8B%E0%B9%88%E0%B8%9A%E0%B8%A7%E0%B8%B1%E0%B8%99-%E0%B8%95%E0%B8%B3%E0%B8%8B%E0%B8%B1%E0%B9%88%E0%B8%A7-original", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_204285", "name": "ปัญญาไก่มะระ สีลม", "cuisine": "Street-Food", "area": "Silom", "type": "street-food", "budget": 1, "budgetLabel": "฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 9, "newReviews30d": -82, "velocityPct": -90.1, "tags": ["street-food", "silom", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": false, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/204285gc-%E0%B8%9B%E0%B8%B1%E0%B8%8D%E0%B8%8D%E0%B8%B2%E0%B9%84%E0%B8%81%E0%B9%88%E0%B8%A1%E0%B8%B0%E0%B8%A3%E0%B8%B0-%E0%B8%AA%E0%B8%B5%E0%B8%A5%E0%B8%A1", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_989481", "name": "Honaji Ramen เซ็นทรัล พระราม 9", "cuisine": "Other", "area": "Rama 9", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 15, "newReviews30d": -97, "velocityPct": -86.6, "tags": ["other", "rama9", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/989481gt-honaji-ramen-%E0%B9%80%E0%B8%8B%E0%B9%87%E0%B8%99%E0%B8%97%E0%B8%A3%E0%B8%B1%E0%B8%A5-%E0%B8%9E%E0%B8%A3%E0%B8%B0%E0%B8%A3%E0%B8%B2%E0%B8%A1-9", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_2459", "name": "บ้านยาย โชคชัย 4", "cuisine": "Thai", "area": "Lat Phrao", "type": "thai", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 112, "newReviews30d": -107, "velocityPct": -48.9, "tags": ["thai", "ladprao", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/baanyay", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_374308", "name": "หมูปิ้งลุงอ้วน สีลม หมูปิ้งโบราณ สาทร", "cuisine": "Thai", "area": "Silom", "type": "thai", "budget": 1, "budgetLabel": "฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 64, "newReviews30d": -107, "velocityPct": -62.6, "tags": ["thai", "silom", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/374308VK-%E0%B8%AB%E0%B8%A1%E0%B8%B9%E0%B8%9B%E0%B8%B4%E0%B9%89%E0%B8%87%E0%B8%A5%E0%B8%B8%E0%B8%87%E0%B8%AD%E0%B9%89%E0%B8%A7%E0%B8%99-%E0%B8%AA%E0%B8%B5%E0%B8%A5%E0%B8%A1-%E0%B8%AB%E0%B8%A1%E0%B8%B9%E0%B8%9B%E0%B8%B4%E0%B9%89%E0%B8%87%E0%B9%82%E0%B8%9A%E0%B8%A3%E0%B8%B2%E0%B8%93-%E0%B8%AA%E0%B8%B2%E0%B8%97%E0%B8%A3-sathorn", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_148423", "name": "KIN SOMTUM   กิน ส้มตำ เหม่งจ๋าย", "cuisine": "Thai", "area": "Ratchada", "type": "thai", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 26, "newReviews30d": -109, "velocityPct": -80.7, "tags": ["thai", "ratchada", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/148423Xd-kin-somtum-%E0%B8%81%E0%B8%B4%E0%B8%99-%E0%B8%AA%E0%B9%89%E0%B8%A1%E0%B8%95%E0%B8%B3-%E0%B9%80%E0%B8%AB%E0%B8%A1%E0%B9%88%E0%B8%87%E0%B8%88%E0%B9%8B%E0%B8%B2%E0%B8%A2", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_184170", "name": "เรือนแม่หลุย ฟอร์จูน ทาวน์", "cuisine": "Thai", "area": "Rama 9", "type": "thai", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 70, "newReviews30d": -111, "velocityPct": -61.3, "tags": ["thai", "rama9", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/184170rE-%E0%B9%80%E0%B8%A3%E0%B8%B7%E0%B8%AD%E0%B8%99%E0%B9%81%E0%B8%A1%E0%B9%88%E0%B8%AB%E0%B8%A5%E0%B8%B8%E0%B8%A2-%E0%B8%9F%E0%B8%AD%E0%B8%A3%E0%B9%8C%E0%B8%88%E0%B8%B9%E0%B8%99-%E0%B8%97%E0%B8%B2%E0%B8%A7%E0%B8%99%E0%B9%8C", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_2334643KA", "name": "อาเล็กโภชนา พุทธมณฑลสาย3", "cuisine": "Other", "area": "On Nut", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -111, "velocityPct": -100.0, "tags": ["other", "onnut", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/2334643KA-%E0%B8%AD%E0%B8%B2%E0%B9%80%E0%B8%A5%E0%B9%87%E0%B8%81%E0%B9%82%E0%B8%A0%E0%B8%8A%E0%B8%99%E0%B8%B2-%E0%B8%9E%E0%B8%B8%E0%B8%97%E0%B8%98%E0%B8%A1%E0%B8%93%E0%B8%91%E0%B8%A5%E0%B8%AA%E0%B8%B2%E0%B8%A23?_st=cD04O2I9MjMzNDY0MzthZD1mYWxzZTt0PTE3NzUzNzk1NzE4Mjk7cmk9MVg3YlZ0R2JQVnR0bktzakwwR3VKc3pDNWVBakd1O2k9MVg3MHpEMkJ1WGxRcEpXMXJhQko1VkVLdUJ4MWoyO3dyZWY9c3I7", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_532950", "name": "OCCA’S -", "cuisine": "Cafe", "area": "Ekkamai", "type": "cafe", "budget": 4, "budgetLabel": "฿฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 34, "newReviews30d": -120, "velocityPct": -77.9, "tags": ["cafe", "ekkamai", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": false, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/532950Sq-occa-s", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_2507850", "name": "Yakiniku Like Central Rama9", "cuisine": "Japanese", "area": "Rama 9", "type": "japanese", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 9, "newReviews30d": -132, "velocityPct": -93.6, "tags": ["japanese", "rama9", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/2507850eh-yakiniku-like-central-rama9", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_2781829", "name": "Meet Moon จี ทาวเวอร์", "cuisine": "Japanese", "area": "Rama 9", "type": "japanese", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 15, "newReviews30d": -139, "velocityPct": -90.3, "tags": ["japanese", "rama9", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/2781829Ah-meet-moon-%E0%B8%88%E0%B8%B5-%E0%B8%97%E0%B8%B2%E0%B8%A7%E0%B9%80%E0%B8%A7%E0%B8%AD%E0%B8%A3%E0%B9%8C", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_431147", "name": "Arvie พระราม3", "cuisine": "Thai", "area": "Sukhumvit", "type": "thai", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 32, "newReviews30d": -142, "velocityPct": -81.6, "tags": ["thai", "sukhumvit", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/431147Lz-arvie-%E0%B8%9E%E0%B8%A3%E0%B8%B0%E0%B8%A3%E0%B8%B2%E0%B8%A13", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_323794", "name": "จุ่มแซ่บ L A รัชดา", "cuisine": "Isaan", "area": "Ratchada", "type": "isaan", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 45, "newReviews30d": -151, "velocityPct": -77.0, "tags": ["isaan", "ratchada", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/323794hy-%E0%B8%88%E0%B8%B8%E0%B9%88%E0%B8%A1%E0%B9%81%E0%B8%8B%E0%B9%88%E0%B8%9A-l-a-%E0%B8%A3%E0%B8%B1%E0%B8%8A%E0%B8%94%E0%B8%B2", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_1957640", "name": "Saemaeul (แซมาอึล) เซ็นทรัลพระราม9", "cuisine": "Korean", "area": "Rama 9", "type": "korean", "budget": 4, "budgetLabel": "฿฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 24, "newReviews30d": -157, "velocityPct": -86.7, "tags": ["korean", "rama9", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/1957640KI-saemaeul-%E0%B9%81%E0%B8%8B%E0%B8%A1%E0%B8%B2%E0%B8%AD%E0%B8%B6%E0%B8%A5-%E0%B9%80%E0%B8%8B%E0%B9%87%E0%B8%99%E0%B8%97%E0%B8%A3%E0%B8%B1%E0%B8%A5%E0%B8%9E%E0%B8%A3%E0%B8%B0%E0%B8%A3%E0%B8%B2%E0%B8%A19-central-rama9", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_185989", "name": "Saladburi", "cuisine": "Other", "area": "Rama 9", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 52, "newReviews30d": -161, "velocityPct": -75.6, "tags": ["other", "rama9", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/185989Un-saladburi", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_3011225yc", "name": "หอมด่วน สีลม", "cuisine": "Other", "area": "Ari", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -169, "velocityPct": -100.0, "tags": ["other", "ari", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/3011225yc-%E0%B8%AB%E0%B8%AD%E0%B8%A1%E0%B8%94%E0%B9%88%E0%B8%A7%E0%B8%99-%E0%B8%AA%E0%B8%B5%E0%B8%A5%E0%B8%A1?_st=cD03O2I9MzAxMTIyNTthZD1mYWxzZTt0PTE3NzUzNzk1NjY0NjI7cmk9MVg3YlZ0R2FqbGNYd3JMVlJBWVhXbENlUndwbGtXO2k9MVg3MHpEMkJKVkl1TlBoMnB5c3ZrZmxZeDJhVVJPO3dyZWY9c3I7", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_1589218kz", "name": "the key room 72", "cuisine": "Other", "area": "Ari", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -180, "velocityPct": -100.0, "tags": ["other", "ari", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/1589218kz-the-key-room-72", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_13658", "name": "Won Korean Restaurant - ถนน รัชดาภิเษก รัชดาภิเษก", "cuisine": "Korean", "area": "Ratchada", "type": "korean", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 76, "newReviews30d": -182, "velocityPct": -70.5, "tags": ["korean", "ratchada", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/13658hW-won-korean-restaurant-%E0%B8%96%E0%B8%99%E0%B8%99-%E0%B8%A3%E0%B8%B1%E0%B8%8A%E0%B8%94%E0%B8%B2%E0%B8%A0%E0%B8%B4%E0%B9%80%E0%B8%A9%E0%B8%81-%E0%B8%A3%E0%B8%B1%E0%B8%8A%E0%B8%94%E0%B8%B2%E0%B8%A0%E0%B8%B4%E0%B9%80%E0%B8%A9%E0%B8%81", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_138064", "name": "Umenohana นิฮอนมูระมอลล์", "cuisine": "Japanese", "area": "Thonglor", "type": "japanese", "budget": 4, "budgetLabel": "฿฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 169, "newReviews30d": -187, "velocityPct": -52.5, "tags": ["japanese", "thonglor", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/umenohana", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_153843", "name": "ร้านทะเลทอด ศาลาแดง", "cuisine": "Street-Food", "area": "Silom", "type": "street-food", "budget": 1, "budgetLabel": "฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 80, "newReviews30d": -201, "velocityPct": -71.5, "tags": ["street-food", "silom", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": false, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/153843SW-%E0%B8%A3%E0%B9%89%E0%B8%B2%E0%B8%99%E0%B8%97%E0%B8%B0%E0%B9%80%E0%B8%A5%E0%B8%97%E0%B8%AD%E0%B8%94-%E0%B8%A8%E0%B8%B2%E0%B8%A5%E0%B8%B2%E0%B9%81%E0%B8%94%E0%B8%87", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_54738JF", "name": "pizza hut บางรัก", "cuisine": "Italian", "area": "Sathorn", "type": "italian", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -207, "velocityPct": -100.0, "tags": ["italian", "sathorn", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/54738JF-pizza-hut-%E0%B8%9A%E0%B8%B2%E0%B8%87%E0%B8%A3%E0%B8%B1%E0%B8%81?_st=cD0zO2I9NTQ3Mzg7YWQ9ZmFsc2U7dD0xNzc1Mzc5NTY0NzA2O3JpPTFYN2JWdEdhVm5oZ0QxM2JCMWJ1VHJiNnVVWHU1dTtpPTFYNzB6RDJBek94ckZxMzZaVVlPandIaWhLTVhQbjt3cmVmPXNyOw%3D%3D", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_2614457Sh", "name": "peter s pan kitchen บางแค", "cuisine": "Other", "area": "On Nut", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -209, "velocityPct": -100.0, "tags": ["other", "onnut", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/2614457Sh-peter-s-pan-kitchen-%E0%B8%9A%E0%B8%B2%E0%B8%87%E0%B9%81%E0%B8%84?_st=cD01O2I9MjYxNDQ1NzthZD1mYWxzZTt0PTE3NzUzNzk1NzE4Mjg7cmk9MVg3YlZ0R2JMOEdpcGpHRDdsNXRLM2tIQngzMnE1O2k9MVg3MHpEMkJ1WGxRcEpXMXJhQko1VkVLdUJ4MWoyO3dyZWY9c3I7", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_14498", "name": "Spaghetti Factory Central Plaza Grand Rama 9", "cuisine": "Italian", "area": "Rama 9", "type": "italian", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 125, "newReviews30d": -213, "velocityPct": -63.0, "tags": ["italian", "rama9", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/spaghetti-factory-rama9", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_2955344", "name": "นุ่มจัด noomjad.bkk - สเต๊ก Steak พาสต้า Pasta อาหารจานเดียว G Tower พระราม 9 ชั้น G", "cuisine": "Japanese", "area": "Rama 9", "type": "japanese", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 13, "newReviews30d": -232, "velocityPct": -94.7, "tags": ["japanese", "rama9", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/2955344em-%E0%B8%99%E0%B8%B8%E0%B9%88%E0%B8%A1%E0%B8%88%E0%B8%B1%E0%B8%94-noomjad-bkk-%E0%B8%AA%E0%B9%80%E0%B8%95%E0%B9%8A%E0%B8%81-steak-%E0%B8%9E%E0%B8%B2%E0%B8%AA%E0%B8%95%E0%B9%89%E0%B8%B2-pasta-%E0%B8%AD%E0%B8%B2%E0%B8%AB%E0%B8%B2%E0%B8%A3%E0%B8%88%E0%B8%B2%E0%B8%99%E0%B9%80%E0%B8%94%E0%B8%B5%E0%B8%A2%E0%B8%A7-g-tower-%E0%B8%9E%E0%B8%A3%E0%B8%B0%E0%B8%A3%E0%B8%B2%E0%B8%A1-9-%E0%B8%8A%E0%B8%B1%E0%B9%89%E0%B8%99-g", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_2986", "name": "Loong Foong สวิสโฮเต็ล กรุงเทพฯ รัชดา", "cuisine": "Other", "area": "Ratchada", "type": "other", "budget": 4, "budgetLabel": "฿฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 103, "newReviews30d": -248, "velocityPct": -70.7, "tags": ["other", "ratchada", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/listings/ratchada-restaurants#2986", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_306933", "name": "โอชาม ข้าวต้มแห้ง เอกมัย", "cuisine": "Other", "area": "Ekkamai", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 67, "newReviews30d": -263, "velocityPct": -79.7, "tags": ["other", "ekkamai", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/306933ce-%E0%B9%82%E0%B8%AD%E0%B8%8A%E0%B8%B2%E0%B8%A1-%E0%B8%82%E0%B9%89%E0%B8%B2%E0%B8%A7%E0%B8%95%E0%B9%89%E0%B8%A1%E0%B9%81%E0%B8%AB%E0%B9%89%E0%B8%87-%E0%B9%80%E0%B8%AD%E0%B8%81%E0%B8%A1%E0%B8%B1%E0%B8%A2-ekkamai", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_25439", "name": "Ginzado ทองหล่อ", "cuisine": "Japanese", "area": "Thonglor", "type": "japanese", "budget": 4, "budgetLabel": "฿฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 187, "newReviews30d": -268, "velocityPct": -58.9, "tags": ["japanese", "thonglor", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/listings/restaurants-in-thonglor#25439", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_1924570", "name": "KINKI Japanese Progressive Dining &amp; Bar ทองหล่อ", "cuisine": "Japanese", "area": "Thonglor", "type": "japanese", "budget": 4, "budgetLabel": "฿฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 122, "newReviews30d": -276, "velocityPct": -69.3, "tags": ["japanese", "thonglor", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/1924570Rh-kinki-japanese-progressive-dining-bar-%E0%B8%97%E0%B8%AD%E0%B8%87%E0%B8%AB%E0%B8%A5%E0%B9%88%E0%B8%AD", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_1968048Ao", "name": "brekky s brunch healthy lunch สาทร", "cuisine": "Other", "area": "Sathorn", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -283, "velocityPct": -100.0, "tags": ["other", "sathorn", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/1968048Ao-brekky-s-brunch-healthy-lunch-%E0%B8%AA%E0%B8%B2%E0%B8%97%E0%B8%A3?_st=cD05O2I9MTk2ODA0ODthZD1mYWxzZTt0PTE3NzUzNzk1NjQ3MTE7cmk9MVg3YlZ0R2FSVWtFUXoxalp3Q1JoZXQ0TnNoU01OO2k9MVg3MHpEMkF6T3hyRnEzNlpVWU9qd0hpaEtNWFBuO3dyZWY9c3I7", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_269651", "name": "เมืองกรุง ก๋วยเตี๋ยวไก่มะระ วังหิน", "cuisine": "Other", "area": "Lat Phrao", "type": "other", "budget": 1, "budgetLabel": "฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 14, "newReviews30d": -299, "velocityPct": -95.5, "tags": ["other", "ladprao", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/269651JF-%E0%B9%80%E0%B8%A1%E0%B8%B7%E0%B8%AD%E0%B8%87%E0%B8%81%E0%B8%A3%E0%B8%B8%E0%B8%87-%E0%B8%81%E0%B9%8B%E0%B8%A7%E0%B8%A2%E0%B9%80%E0%B8%95%E0%B8%B5%E0%B9%8B%E0%B8%A2%E0%B8%A7%E0%B9%84%E0%B8%81%E0%B9%88%E0%B8%A1%E0%B8%B0%E0%B8%A3%E0%B8%B0-%E0%B8%A7%E0%B8%B1%E0%B8%87%E0%B8%AB%E0%B8%B4%E0%B8%99", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_400460", "name": "CHUNN ฉัน Ekamai", "cuisine": "Casual", "area": "Ekkamai", "type": "casual", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 90, "newReviews30d": -353, "velocityPct": -79.7, "tags": ["casual", "ekkamai", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": false, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/400460fP-chunn-%E0%B8%89%E0%B8%B1%E0%B8%99-ekamai", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_25068", "name": "OSAKA OHSHO (โอซาก้า โอโช) – Thonglor ฟิฟท์ตี้ฟิฟท์ ทองหล่อ", "cuisine": "Japanese", "area": "Thonglor", "type": "japanese", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 72, "newReviews30d": -358, "velocityPct": -83.3, "tags": ["japanese", "thonglor", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/25068Td-osaka-ohsho-%E0%B9%82%E0%B8%AD%E0%B8%8B%E0%B8%B2%E0%B8%81%E0%B9%89%E0%B8%B2-%E0%B9%82%E0%B8%AD%E0%B9%82%E0%B8%8A-thonglor", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_5364", "name": "อากาเว่ (ฟูมุ่ยกี่ 2)", "cuisine": "Other", "area": "Rama 9", "type": "other", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 97, "newReviews30d": -380, "velocityPct": -79.7, "tags": ["other", "rama9", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/5364xN-%E0%B8%AD%E0%B8%B2%E0%B8%81%E0%B8%B2%E0%B9%80%E0%B8%A7%E0%B9%88-%E0%B8%9F%E0%B8%B9%E0%B8%A1%E0%B8%B8%E0%B9%88%E0%B8%A2%E0%B8%81%E0%B8%B5%E0%B9%88-2", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_686021pQ", "name": "ginprik กินพริก พุทธมณฑล สาย3", "cuisine": "Other", "area": "On Nut", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -387, "velocityPct": -100.0, "tags": ["other", "onnut", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/686021pQ-ginprik-%E0%B8%81%E0%B8%B4%E0%B8%99%E0%B8%9E%E0%B8%A3%E0%B8%B4%E0%B8%81-%E0%B8%9E%E0%B8%B8%E0%B8%97%E0%B8%98%E0%B8%A1%E0%B8%93%E0%B8%91%E0%B8%A5-%E0%B8%AA%E0%B8%B2%E0%B8%A23?_st=cD02O2I9Njg2MDIxO2FkPWZhbHNlO3Q9MTc3NTM3OTU3MTgyODtyaT0xWDdiVnRHYks3V0wzUldubXBhSGQwUkZSQzd1OVM7aT0xWDcwekQyQnVYbFFwSlcxcmFCSjVWRUt1QngxajI7d3JlZj1zcjs%3D", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_964186", "name": "Jones&apos; Salad central พระราม9", "cuisine": "Other", "area": "Rama 9", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 15, "newReviews30d": -392, "velocityPct": -96.3, "tags": ["other", "rama9", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/listings/must-try-restaurants-at-rama9#964186", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_70352", "name": "Paesano Italian Restaurant(ภัตตาคารไพซาโน่) ลาดพร้าว 71 (ซ.นาคนิวาส5)", "cuisine": "Italian", "area": "Lat Phrao", "type": "italian", "budget": 4, "budgetLabel": "฿฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 43, "newReviews30d": -395, "velocityPct": -90.2, "tags": ["italian", "ladprao", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/70352ZJ-paesano-italian-restaurant-%E0%B8%A0%E0%B8%B1%E0%B8%95%E0%B8%95%E0%B8%B2%E0%B8%84%E0%B8%B2%E0%B8%A3%E0%B9%84%E0%B8%9E%E0%B8%8B%E0%B8%B2%E0%B9%82%E0%B8%99%E0%B9%88-%E0%B8%A5%E0%B8%B2%E0%B8%94%E0%B8%9E%E0%B8%A3%E0%B9%89%E0%B8%B2%E0%B8%A7-71-%E0%B8%8B-%E0%B8%99%E0%B8%B2%E0%B8%84%E0%B8%99%E0%B8%B4%E0%B8%A7%E0%B8%B2%E0%B8%AA5", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_190200", "name": "บ้านสุขนิยม", "cuisine": "Thai", "area": "Ratchada", "type": "thai", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 18, "newReviews30d": -417, "velocityPct": -95.9, "tags": ["thai", "ratchada", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/listings/ratchada-restaurants#190200", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_9640", "name": "เลิศทิพย์. เลิศทิพย์วังหิน", "cuisine": "Other", "area": "Lat Phrao", "type": "other", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 143, "newReviews30d": -423, "velocityPct": -74.7, "tags": ["other", "ladprao", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/9640Ev-%E0%B9%80%E0%B8%A5%E0%B8%B4%E0%B8%A8%E0%B8%97%E0%B8%B4%E0%B8%9E%E0%B8%A2%E0%B9%8C-%E0%B9%80%E0%B8%A5%E0%B8%B4%E0%B8%A8%E0%B8%97%E0%B8%B4%E0%B8%9E%E0%B8%A2%E0%B9%8C%E0%B8%A7%E0%B8%B1%E0%B8%87%E0%B8%AB%E0%B8%B4%E0%B8%99", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_1485471", "name": "the sparrow pizza studio เอกมัย", "cuisine": "Italian", "area": "Ekkamai", "type": "italian", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 17, "newReviews30d": -426, "velocityPct": -96.2, "tags": ["italian", "ekkamai", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/1485471Ha-the-sparrow-pizza-studio-%E0%B9%80%E0%B8%AD%E0%B8%81%E0%B8%A1%E0%B8%B1%E0%B8%A2-identical", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_270539", "name": "DalDal Korean Restaurant G Tower", "cuisine": "Korean", "area": "Rama 9", "type": "korean", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 38, "newReviews30d": -429, "velocityPct": -91.9, "tags": ["korean", "rama9", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/270539HA-daldal-korean-restaurant-g-tower", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_314119", "name": "Délices de capoue", "cuisine": "Italian", "area": "Ekkamai", "type": "italian", "budget": 4, "budgetLabel": "฿฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 25, "newReviews30d": -433, "velocityPct": -94.5, "tags": ["italian", "ekkamai", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/314119AD-d%C3%A9lices-de-capoue", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_716473", "name": "Gen Japanese Charcoal Grill Restaurant &amp; Bar เอกมัย", "cuisine": "Japanese", "area": "Ekkamai", "type": "japanese", "budget": 4, "budgetLabel": "฿฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 28, "newReviews30d": -435, "velocityPct": -94.0, "tags": ["japanese", "ekkamai", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/716473Mz-gen-japanese-charcoal-grill-restaurant-bar-%E0%B9%80%E0%B8%AD%E0%B8%81%E0%B8%A1%E0%B8%B1%E0%B8%A2-ekkamai", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_236867", "name": "Nanalee Korean Bbq &amp; Restaurant สี่แยกวังหิน", "cuisine": "Korean", "area": "Lat Phrao", "type": "korean", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 61, "newReviews30d": -438, "velocityPct": -87.8, "tags": ["korean", "ladprao", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/236867tH-nanalee-korean-bbq-restaurant-%E0%B8%AA%E0%B8%B5%E0%B9%88%E0%B9%81%E0%B8%A2%E0%B8%81%E0%B8%A7%E0%B8%B1%E0%B8%87%E0%B8%AB%E0%B8%B4%E0%B8%99", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_183491", "name": "Tai He Xuan", "cuisine": "Other", "area": "Thonglor", "type": "other", "budget": 4, "budgetLabel": "฿฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 153, "newReviews30d": -444, "velocityPct": -74.4, "tags": ["other", "thonglor", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/183491PT-tai-he-xuan", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_9210", "name": "เครป พรพิมล (เครปป้าเฉื่อย/เครปชาติหน้า)", "cuisine": "Other", "area": "Lat Phrao", "type": "other", "budget": 1, "budgetLabel": "฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 75, "newReviews30d": -446, "velocityPct": -85.6, "tags": ["other", "ladprao", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/listings/ladprao-restaurants#9210", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_188550", "name": "บ้านเพื่อน เอกมัย", "cuisine": "Thai", "area": "Sukhumvit", "type": "thai", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 31, "newReviews30d": -455, "velocityPct": -93.6, "tags": ["thai", "sukhumvit", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/188550uZ-%E0%B8%9A%E0%B9%89%E0%B8%B2%E0%B8%99%E0%B9%80%E0%B8%9E%E0%B8%B7%E0%B9%88%E0%B8%AD%E0%B8%99-ekkamai", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_617114dR", "name": "pink typhoon creative pasta steak ari พิ้งค์ ไต้ฝุ่น ครีเอทีฟ พาสต้า สเต๊ก อารีย", "cuisine": "Steakhouse", "area": "Ari", "type": "steakhouse", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -457, "velocityPct": -100.0, "tags": ["steakhouse", "ari", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/617114dR-pink-typhoon-creative-pasta-steak-ari-%E0%B8%9E%E0%B8%B4%E0%B9%89%E0%B8%87%E0%B8%84%E0%B9%8C-%E0%B9%84%E0%B8%95%E0%B9%89%E0%B8%9D%E0%B8%B8%E0%B9%88%E0%B8%99-%E0%B8%84%E0%B8%A3%E0%B8%B5%E0%B9%80%E0%B8%AD%E0%B8%97%E0%B8%B5%E0%B8%9F-%E0%B8%9E%E0%B8%B2%E0%B8%AA%E0%B8%95%E0%B9%89%E0%B8%B2-%E0%B8%AA%E0%B9%80%E0%B8%95%E0%B9%8A%E0%B8%81-%E0%B8%AD%E0%B8%B2%E0%B8%A3%E0%B8%B5%E0%B8%A2%E0%B9%8C-pink-typhoon-creative-pasta-steak-ari-%E0%B8%9E%E0%B8%B4%E0%B9%89%E0%B8%87%E0%B8%84%E0%B9%8C-%E0%B9%84%E0%B8%95%E0%B9%89%E0%B8%9D%E0%B8%B8%E0%B9%88%E0%B8%99-%E0%B8%84%E0%B8%A3%E0%B8%B5%E0%B9%80%E0%B8%AD%E0%B8%97%E0%B8%B5%E0%B8%9F-%E0%B8%9E%E0%B8%B2%E0%B8%AA%E0%B8%95%E0%B9%89%E0%B8%B2-%E0%B8%AA%E0%B9%80%E0%B8%95%E0%B9%8A%E0%B8%81-%E0%B8%AD%E0%B8%B2%E0%B8%A3%E0%B8%B5%E0%B8%A2%E0%B9%8C?_st=cD05O2I9NjE3MTE0O2FkPWZhbHNlO3Q9MTc3NTM3OTU2NjQ2MjtyaT0xWDdiVnRHYW1sWHBsZ3hESk1zWnlrQ1pSenVMNlU7aT0xWDcwekQyQkpWSXVOUGgycHlzdmtmbFl4MmFVUk87d3JlZj1zcjs%3D", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_8532", "name": "โกวใหญ่", "cuisine": "Other", "area": "Lat Phrao", "type": "other", "budget": 1, "budgetLabel": "฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 69, "newReviews30d": -471, "velocityPct": -87.2, "tags": ["other", "ladprao", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/8532LK-%E0%B9%82%E0%B8%81%E0%B8%A7%E0%B9%83%E0%B8%AB%E0%B8%8D%E0%B9%88", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_7025", "name": "Mellow Restaurant &amp; Bar Penny&apos;s Balcony ทองหล่อ 16", "cuisine": "Other", "area": "Sukhumvit", "type": "other", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 91, "newReviews30d": -495, "velocityPct": -84.5, "tags": ["other", "sukhumvit", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/7025XK-mellow-restaurant-bar-penny-s-balcony-%E0%B8%97%E0%B8%AD%E0%B8%87%E0%B8%AB%E0%B8%A5%E0%B9%88%E0%B8%AD-16", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_14301", "name": "On the Table เซ็นทรัลพลาซ่า พระราม 9", "cuisine": "Other", "area": "Rama 9", "type": "other", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 187, "newReviews30d": -498, "velocityPct": -72.7, "tags": ["other", "rama9", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/onthetable-centra-rama9", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_215404", "name": "Taishoken Ramen", "cuisine": "Japanese", "area": "Thonglor", "type": "japanese", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 83, "newReviews30d": -582, "velocityPct": -87.5, "tags": ["japanese", "thonglor", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/215404kX-taishoken-ramen", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_171586", "name": "สมยงตำซั่ว2 พระราม 9", "cuisine": "Isaan", "area": "Rama 9", "type": "isaan", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 54, "newReviews30d": -600, "velocityPct": -91.7, "tags": ["isaan", "rama9", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/171586xD-%E0%B8%AA%E0%B8%A1%E0%B8%A2%E0%B8%87%E0%B8%95%E0%B8%B3%E0%B8%8B%E0%B8%B1%E0%B9%88%E0%B8%A72-%E0%B8%9E%E0%B8%A3%E0%B8%B0%E0%B8%A3%E0%B8%B2%E0%B8%A1-9-rama-9", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_329407", "name": "Bookmagol 북막골 เอกมัย (Ekkamai)", "cuisine": "Korean", "area": "Ekkamai", "type": "korean", "budget": 4, "budgetLabel": "฿฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 65, "newReviews30d": -605, "velocityPct": -90.3, "tags": ["korean", "ekkamai", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/329407WS-bookmagol-%EB%B6%81%EB%A7%89%EA%B3%A8-%E0%B9%80%E0%B8%AD%E0%B8%81%E0%B8%A1%E0%B8%B1%E0%B8%A2-ekkamai", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_187608Pt", "name": "hanazen", "cuisine": "Other", "area": "Ari", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -613, "velocityPct": -100.0, "tags": ["other", "ari", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/187608Pt-hanazen?_st=cD04O2I9MTg3NjA4O2FkPWZhbHNlO3Q9MTc3NTM3OTU2NjQ2MjtyaT0xWDdiVnRHYWx3bHU5emFCN3F1QzRCTE1yTkFZb3Y7aT0xWDcwekQyQkpWSXVOUGgycHlzdmtmbFl4MmFVUk87d3JlZj1zcjs%3D", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_741749", "name": "69 Rock Men ทองหล่อ", "cuisine": "Other", "area": "Thonglor", "type": "other", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 54, "newReviews30d": -655, "velocityPct": -92.4, "tags": ["other", "thonglor", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/741749ao-69-rock-men-%E0%B8%97%E0%B8%AD%E0%B8%87%E0%B8%AB%E0%B8%A5%E0%B9%88%E0%B8%AD-thonglor", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_34", "name": "บุญตงเกียรติ ข้าวมันไก่สิงคโปร์ ทองหล่อ", "cuisine": "Other", "area": "Thonglor", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 176, "newReviews30d": -671, "velocityPct": -79.2, "tags": ["other", "thonglor", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/34Iu-%E0%B8%9A%E0%B8%B8%E0%B8%8D%E0%B8%95%E0%B8%87%E0%B9%80%E0%B8%81%E0%B8%B5%E0%B8%A2%E0%B8%A3%E0%B8%95%E0%B8%B4-%E0%B8%82%E0%B9%89%E0%B8%B2%E0%B8%A7%E0%B8%A1%E0%B8%B1%E0%B8%99%E0%B9%84%E0%B8%81%E0%B9%88%E0%B8%AA%E0%B8%B4%E0%B8%87%E0%B8%84%E0%B9%82%E0%B8%9B%E0%B8%A3%E0%B9%8C-%E0%B8%97%E0%B8%AD%E0%B8%87%E0%B8%AB%E0%B8%A5%E0%B9%88%E0%B8%AD-thonglor", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_229796", "name": "อาหารใต้ บ้านฉลอง Baan Chalong", "cuisine": "Other", "area": "Lat Phrao", "type": "other", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 88, "newReviews30d": -685, "velocityPct": -88.6, "tags": ["other", "ladprao", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/229796dt-%E0%B8%AD%E0%B8%B2%E0%B8%AB%E0%B8%B2%E0%B8%A3%E0%B9%83%E0%B8%95%E0%B9%89-%E0%B8%9A%E0%B9%89%E0%B8%B2%E0%B8%99%E0%B8%89%E0%B8%A5%E0%B8%AD%E0%B8%87-baan-chalong", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_174574", "name": "ครัวคุณอิ้น ซอยประดิษฐมนูธรรม 23", "cuisine": "Other", "area": "Lat Phrao", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 61, "newReviews30d": -692, "velocityPct": -91.9, "tags": ["other", "ladprao", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/174574Ih-%E0%B8%84%E0%B8%A3%E0%B8%B1%E0%B8%A7%E0%B8%84%E0%B8%B8%E0%B8%93%E0%B8%AD%E0%B8%B4%E0%B9%89%E0%B8%99-%E0%B8%8B%E0%B8%AD%E0%B8%A2%E0%B8%9B%E0%B8%A3%E0%B8%B0%E0%B8%94%E0%B8%B4%E0%B8%A9%E0%B8%90%E0%B8%A1%E0%B8%99%E0%B8%B9%E0%B8%98%E0%B8%A3%E0%B8%A3%E0%B8%A1-23", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_14055", "name": "เฝอ 54  ลาดพร้าววังหิน", "cuisine": "Other", "area": "Lat Phrao", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 218, "newReviews30d": -697, "velocityPct": -76.2, "tags": ["other", "ladprao", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/pho54-wanghin", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_367219", "name": "Bangkok Banjom เอกมัย", "cuisine": "Korean", "area": "Ekkamai", "type": "korean", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 24, "newReviews30d": -796, "velocityPct": -97.1, "tags": ["korean", "ekkamai", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/367219mm-bangkok-banjom-%E0%B9%80%E0%B8%AD%E0%B8%81%E0%B8%A1%E0%B8%B1%E0%B8%A2-ekkamai", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_3065427GG", "name": "zoom sky bar 2 2", "cuisine": "Other", "area": "Sathorn", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -825, "velocityPct": -100.0, "tags": ["other", "sathorn", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/3065427GG-zoom-sky-bar-2-2?_st=cD02O2I9MzA2NTQyNzthZD1mYWxzZTt0PTE3NzUzNzk1NjQ3MDk7cmk9MVg3YlZ0R2FXalJneVRLRUx4NGxzTjBISTdRbDl4O2k9MVg3MHpEMkF6T3hyRnEzNlpVWU9qd0hpaEtNWFBuO3dyZWY9c3I7", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_1699283Ly", "name": "โคตรเฮงสาย2", "cuisine": "Other", "area": "On Nut", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -834, "velocityPct": -100.0, "tags": ["other", "onnut", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/1699283Ly-%E0%B9%82%E0%B8%84%E0%B8%95%E0%B8%A3%E0%B9%80%E0%B8%AE%E0%B8%87%E0%B8%AA%E0%B8%B2%E0%B8%A22?_st=cD0wO2I9MTY5OTI4MzthZD1mYWxzZTt0PTE3NzUzNzk1NzE4MTY7cmk9MVg3YlZ0R2JPdTNzWFN5aDdxTzF6Vm9qeUszWGVpO2k9MVg3MHpEMkJ1WGxRcEpXMXJhQko1VkVLdUJ4MWoyO3dyZWY9c3I7", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_3566578gK", "name": "คลั่งเนื้อ อารีย์ซอย 5 klang nuea", "cuisine": "Other", "area": "Ari", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -852, "velocityPct": -100.0, "tags": ["other", "ari", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/3566578gK-%E0%B8%84%E0%B8%A5%E0%B8%B1%E0%B9%88%E0%B8%87%E0%B9%80%E0%B8%99%E0%B8%B7%E0%B9%89%E0%B8%AD-%E0%B8%AD%E0%B8%B2%E0%B8%A3%E0%B8%B5%E0%B8%A2%E0%B9%8C%E0%B8%8B%E0%B8%AD%E0%B8%A2-5-klang-nuea?_st=cD02O2I9MzU2NjU3ODthZD1mYWxzZTt0PTE3NzUzNzk1NjY0NTM7cmk9MVg3YlZ0R2FpWVNQdndXY0JOYXNuMHFNMGdVVENUO2k9MVg3MHpEMkJKVkl1TlBoMnB5c3ZrZmxZeDJhVVJPO3dyZWY9c3I7", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_482215", "name": "Beast &amp; Butter", "cuisine": "Other", "area": "Thonglor", "type": "other", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 50, "newReviews30d": -882, "velocityPct": -94.6, "tags": ["other", "thonglor", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/482215Gy-beast-butter", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_369216", "name": "Washoku Aji Big-C Ekkamai 3F", "cuisine": "Japanese", "area": "Ekkamai", "type": "japanese", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 148, "newReviews30d": -884, "velocityPct": -85.7, "tags": ["japanese", "ekkamai", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/369216Zd-washoku-aji-big-c-ekkamai-3f", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_216028", "name": "Featherstone .", "cuisine": "Italian", "area": "Sukhumvit", "type": "italian", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 82, "newReviews30d": -884, "velocityPct": -91.5, "tags": ["italian", "sukhumvit", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/216028Cx-featherstone", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_121339", "name": "บ้านไอซ์ ทองหล่อ", "cuisine": "Thai", "area": "Thonglor", "type": "thai", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 187, "newReviews30d": -897, "velocityPct": -82.7, "tags": ["thai", "thonglor", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/121339lu-%E0%B8%9A%E0%B9%89%E0%B8%B2%E0%B8%99%E0%B9%84%E0%B8%AD%E0%B8%8B%E0%B9%8C-%E0%B8%97%E0%B8%AD%E0%B8%87%E0%B8%AB%E0%B8%A5%E0%B9%88%E0%B8%AD-thonglor", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_891196", "name": "肉々亭 Shishitei 肉々亭 Shishitei", "cuisine": "Japanese", "area": "Ekkamai", "type": "japanese", "budget": 4, "budgetLabel": "฿฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 57, "newReviews30d": -898, "velocityPct": -94.0, "tags": ["japanese", "ekkamai", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/891196Ok-%E8%82%89%E3%80%85%E4%BA%AD-shishitei-%E8%82%89%E3%80%85%E4%BA%AD-shishitei", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_193602", "name": "Gokfayuen ทองหล่อ", "cuisine": "Other", "area": "Thonglor", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 277, "newReviews30d": -900, "velocityPct": -76.5, "tags": ["other", "thonglor", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/193602PQ-gokfayuen-%E0%B8%97%E0%B8%AD%E0%B8%87%E0%B8%AB%E0%B8%A5%E0%B9%88%E0%B8%AD-thonglor", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_150775", "name": "Kiani ทองหล่อ", "cuisine": "Korean", "area": "Thonglor", "type": "korean", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 280, "newReviews30d": -944, "velocityPct": -77.1, "tags": ["korean", "thonglor", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/kiani", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_321941", "name": "R.HAAN", "cuisine": "Thai", "area": "Thonglor", "type": "thai", "budget": 4, "budgetLabel": "฿฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 57, "newReviews30d": -954, "velocityPct": -94.4, "tags": ["thai", "thonglor", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/321941vV-r-haan", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_24605", "name": "ก๋วยเตี๋ยว ต้มเลือดหมูนายใช้ ลาดพร้าว", "cuisine": "Other", "area": "Lat Phrao", "type": "other", "budget": 1, "budgetLabel": "฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 66, "newReviews30d": -956, "velocityPct": -93.5, "tags": ["other", "ladprao", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/24605Ci-%E0%B8%81%E0%B9%8B%E0%B8%A7%E0%B8%A2%E0%B9%80%E0%B8%95%E0%B8%B5%E0%B9%8B%E0%B8%A2%E0%B8%A7-%E0%B8%95%E0%B9%89%E0%B8%A1%E0%B9%80%E0%B8%A5%E0%B8%B7%E0%B8%AD%E0%B8%94%E0%B8%AB%E0%B8%A1%E0%B8%B9%E0%B8%99%E0%B8%B2%E0%B8%A2%E0%B9%83%E0%B8%8A%E0%B9%89-%E0%B8%A5%E0%B8%B2%E0%B8%94%E0%B8%9E%E0%B8%A3%E0%B9%89%E0%B8%B2%E0%B8%A7-lat-phrao", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_2339389Zn", "name": "fishmonger อารีย์ ari", "cuisine": "Other", "area": "Ari", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -966, "velocityPct": -100.0, "tags": ["other", "ari", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/2339389Zn-fishmonger-%E0%B8%AD%E0%B8%B2%E0%B8%A3%E0%B8%B5%E0%B8%A2%E0%B9%8C-ari?_st=cD01O2I9MjMzOTM4OTthZD1mYWxzZTt0PTE3NzUzNzk1NjY0NTE7cmk9MVg3YlZ0R2FtOTltbzlPcDZUZ0hMTmN5aDA3OWFnO2k9MVg3MHpEMkJKVkl1TlBoMnB5c3ZrZmxZeDJhVVJPO3dyZWY9c3I7", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_2591851CZ", "name": "san rafael cafe ซาน ราฟาเอล", "cuisine": "Cafe", "area": "On Nut", "type": "cafe", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -1069, "velocityPct": -100.0, "tags": ["cafe", "onnut", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": false, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/2591851CZ-san-rafael-cafe-%E0%B8%8B%E0%B8%B2%E0%B8%99-%E0%B8%A3%E0%B8%B2%E0%B8%9F%E0%B8%B2%E0%B9%80%E0%B8%AD%E0%B8%A5?_st=cD00O2I9MjU5MTg1MTthZD1mYWxzZTt0PTE3NzUzNzk1NzE4Mjg7cmk9MVg3YlZ0R2JQdEwyTDhWQXd4VDJzZHdrcnFTTDE3O2k9MVg3MHpEMkJ1WGxRcEpXMXJhQko1VkVLdUJ4MWoyO3dyZWY9c3I7", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_175563", "name": "หน่องริมคลอง ( Nhong Rimklong ) เอกมัย", "cuisine": "Thai", "area": "Ekkamai", "type": "thai", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 297, "newReviews30d": -1099, "velocityPct": -78.7, "tags": ["thai", "ekkamai", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/nhongrimklong", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_397437", "name": "Mother May I", "cuisine": "Thai", "area": "Ekkamai", "type": "thai", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 28, "newReviews30d": -1123, "velocityPct": -97.6, "tags": ["thai", "ekkamai", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/397437DW-mother-may-i", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_16125", "name": "หอมด่วน เอกมัย", "cuisine": "Other", "area": "Ekkamai", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 112, "newReviews30d": -1148, "velocityPct": -91.1, "tags": ["other", "ekkamai", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/16125xW-%E0%B8%AB%E0%B8%AD%E0%B8%A1%E0%B8%94%E0%B9%88%E0%B8%A7%E0%B8%99-%E0%B9%80%E0%B8%AD%E0%B8%81%E0%B8%A1%E0%B8%B1%E0%B8%A2-ekkamai", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_263014", "name": "เขียวไข่กา ลาดพร้าว", "cuisine": "Thai", "area": "Lat Phrao", "type": "thai", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 191, "newReviews30d": -1233, "velocityPct": -86.6, "tags": ["thai", "ladprao", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/263014PN-%E0%B9%80%E0%B8%82%E0%B8%B5%E0%B8%A2%E0%B8%A7%E0%B9%84%E0%B8%82%E0%B9%88%E0%B8%81%E0%B8%B2-%E0%B8%A5%E0%B8%B2%E0%B8%94%E0%B8%9E%E0%B8%A3%E0%B9%89%E0%B8%B2%E0%B8%A7", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_19635", "name": "อรุณวรรณ เอกมัย", "cuisine": "Other", "area": "Ekkamai", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 207, "newReviews30d": -1264, "velocityPct": -85.9, "tags": ["other", "ekkamai", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/19635qC-%E0%B8%AD%E0%B8%A3%E0%B8%B8%E0%B8%93%E0%B8%A7%E0%B8%A3%E0%B8%A3%E0%B8%93-%E0%B9%80%E0%B8%AD%E0%B8%81%E0%B8%A1%E0%B8%B1%E0%B8%A2-ekkamai", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_2162472oL", "name": "bartels sathorn sourdough sandwiches coffee juicery สาทร sathorn", "cuisine": "Other", "area": "Sathorn", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -1278, "velocityPct": -100.0, "tags": ["other", "sathorn", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/2162472oL-bartels-sathorn-sourdough-sandwiches-coffee-juicery-%E0%B8%AA%E0%B8%B2%E0%B8%97%E0%B8%A3-sathorn?_st=cD0xMDtiPTIxNjI0NzI7YWQ9ZmFsc2U7dD0xNzc1Mzc5NTY0NzEyO3JpPTFYN2JWdEdhVWx2UjBIV2prMkxEOXJSRkVOTmZRcjtpPTFYNzB6RDJBek94ckZxMzZaVVlPandIaWhLTVhQbjt3cmVmPXNyOw%3D%3D", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_1680", "name": "โอว ก๋วยเตี๋ยวพริกสด ซ.มัยลาภ(ย้ายจาก สุคนธสวัสดิ์)", "cuisine": "Other", "area": "Lat Phrao", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 321, "newReviews30d": -1290, "velocityPct": -80.1, "tags": ["other", "ladprao", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/priksodnoodle", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_18579", "name": "คั่วกลิ้ง+ผักสด ทองหล่อ", "cuisine": "Thai", "area": "Thonglor", "type": "thai", "budget": 4, "budgetLabel": "฿฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 147, "newReviews30d": -1338, "velocityPct": -90.1, "tags": ["thai", "thonglor", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/khuakling-thonglor", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_1242896", "name": "SUSHIRO THAILAND Central Plaza Grand Rama 9", "cuisine": "Japanese", "area": "Rama 9", "type": "japanese", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 63, "newReviews30d": -1388, "velocityPct": -95.7, "tags": ["japanese", "rama9", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/1242896jl-sushiro-thailand-central-plaza-grand-rama-9", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_299104", "name": "Khao เอกมัย", "cuisine": "Thai", "area": "Ekkamai", "type": "thai", "budget": 4, "budgetLabel": "฿฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 84, "newReviews30d": -1429, "velocityPct": -94.4, "tags": ["thai", "ekkamai", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/299104eP-khao-%E0%B9%80%E0%B8%AD%E0%B8%81%E0%B8%A1%E0%B8%B1%E0%B8%A2-ekkamai", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_310275", "name": "Escape Bangkok Emquartier", "cuisine": "Other", "area": "Sukhumvit", "type": "other", "budget": 4, "budgetLabel": "฿฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 40, "newReviews30d": -1468, "velocityPct": -97.3, "tags": ["other", "sukhumvit", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/310275jN-escape-bangkok-emquartier", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_873467uH", "name": "lucky s hungry อารีย์", "cuisine": "Other", "area": "Ari", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -1492, "velocityPct": -100.0, "tags": ["other", "ari", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/873467uH-lucky-s-hungry-%E0%B8%AD%E0%B8%B2%E0%B8%A3%E0%B8%B5%E0%B8%A2%E0%B9%8C?_st=cD00O2I9ODczNDY3O2FkPWZhbHNlO3Q9MTc3NTM3OTU2NjQ0MztyaT0xWDdiVnRHYW44QlduMkpPMUpaMU80SDF1b3JZUko7aT0xWDcwekQyQkpWSXVOUGgycHlzdmtmbFl4MmFVUk87d3JlZj1zcjs%3D", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_2458pa", "name": "บ้านพึงชม อารีย์ ari", "cuisine": "Other", "area": "Ari", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -1588, "velocityPct": -100.0, "tags": ["other", "ari", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/2458pa-%E0%B8%9A%E0%B9%89%E0%B8%B2%E0%B8%99%E0%B8%9E%E0%B8%B6%E0%B8%87%E0%B8%8A%E0%B8%A1-%E0%B8%AD%E0%B8%B2%E0%B8%A3%E0%B8%B5%E0%B8%A2%E0%B9%8C-ari", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_123598", "name": "ห้องทานข้าวสุพรรณิการ์ ทองหล่อ ทองหล่อ", "cuisine": "Thai", "area": "Thonglor", "type": "thai", "budget": 4, "budgetLabel": "฿฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 91, "newReviews30d": -1604, "velocityPct": -94.6, "tags": ["thai", "thonglor", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/supannigaeatingroomthonglor", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_149191", "name": "The Gardens of Dinsor Palace", "cuisine": "Italian", "area": "Ekkamai", "type": "italian", "budget": 4, "budgetLabel": "฿฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 125, "newReviews30d": -1652, "velocityPct": -93.0, "tags": ["italian", "ekkamai", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/listings/ekkamai-restaurant#149191", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_63451", "name": "ฮั่วเซ่งฮง เซ็นทรัล พระราม 9", "cuisine": "Other", "area": "Rama 9", "type": "other", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 163, "newReviews30d": -1694, "velocityPct": -91.2, "tags": ["other", "rama9", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/63451So-%E0%B8%AE%E0%B8%B1%E0%B9%88%E0%B8%A7%E0%B9%80%E0%B8%8B%E0%B9%88%E0%B8%87%E0%B8%AE%E0%B8%87-%E0%B9%80%E0%B8%8B%E0%B9%87%E0%B8%99%E0%B8%97%E0%B8%A3%E0%B8%B1%E0%B8%A5-%E0%B8%9E%E0%B8%A3%E0%B8%B0%E0%B8%A3%E0%B8%B2%E0%B8%A1-9", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_253005", "name": "Brewski Rooftop Bar", "cuisine": "Other", "area": "Sukhumvit", "type": "other", "budget": 4, "budgetLabel": "฿฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 21, "newReviews30d": -1697, "velocityPct": -98.8, "tags": ["other", "sukhumvit", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/listings/sukhumvit-restaurants-with-good-atmosphere#253005", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_159446Nb", "name": "via emilia restaurant สาทร sathorn", "cuisine": "Other", "area": "Sathorn", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -1850, "velocityPct": -100.0, "tags": ["other", "sathorn", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/159446Nb-via-emilia-restaurant-%E0%B8%AA%E0%B8%B2%E0%B8%97%E0%B8%A3-sathorn?_st=cD03O2I9MTU5NDQ2O2FkPWZhbHNlO3Q9MTc3NTM3OTU2NDcwOTtyaT0xWDdiVnRHYVZMeE5rd3dTdFBpd3RqZkpEVkZibjg7aT0xWDcwekQyQXpPeHJGcTM2WlVZT2p3SGloS01YUG47d3JlZj1zcjs%3D", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_27363", "name": "สมยศ ข้าวต้มรอบดึก (Som Yot Khaotom Rop Duek)โชคชัย 4 ซอย 72  โชคชัย 4", "cuisine": "Other", "area": "Lat Phrao", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 193, "newReviews30d": -1911, "velocityPct": -90.8, "tags": ["other", "ladprao", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/27363hx-%E0%B8%AA%E0%B8%A1%E0%B8%A2%E0%B8%A8-%E0%B8%82%E0%B9%89%E0%B8%B2%E0%B8%A7%E0%B8%95%E0%B9%89%E0%B8%A1%E0%B8%A3%E0%B8%AD%E0%B8%9A%E0%B8%94%E0%B8%B6%E0%B8%81-som-yot-khaotom-rop-duek-%E0%B9%82%E0%B8%8A%E0%B8%84%E0%B8%8A%E0%B8%B1%E0%B8%A2-4-%E0%B8%8B%E0%B8%AD%E0%B8%A2-72-%E0%B9%82%E0%B8%8A%E0%B8%84%E0%B8%8A%E0%B8%B1%E0%B8%A2-4-chok-chai-4", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_4", "name": "Kosirae", "cuisine": "Korean", "area": "Thonglor", "type": "korean", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 694, "newReviews30d": -2029, "velocityPct": -74.5, "tags": ["korean", "thonglor", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/kosirae", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_575361", "name": "Babyccino คลองตัน", "cuisine": "Cafe", "area": "Ekkamai", "type": "cafe", "budget": 4, "budgetLabel": "฿฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 66, "newReviews30d": -2104, "velocityPct": -97.0, "tags": ["cafe", "ekkamai", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": false, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/575361qw-babyccino", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_65255", "name": "บะหมี่คนแซ่ลี ทองหล่อ", "cuisine": "Other", "area": "Thonglor", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 152, "newReviews30d": -2340, "velocityPct": -93.9, "tags": ["other", "thonglor", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/65255KC-%E0%B8%9A%E0%B8%B0%E0%B8%AB%E0%B8%A1%E0%B8%B5%E0%B9%88%E0%B8%84%E0%B8%99%E0%B9%81%E0%B8%8B%E0%B9%88%E0%B8%A5%E0%B8%B5-%E0%B8%97%E0%B8%AD%E0%B8%87%E0%B8%AB%E0%B8%A5%E0%B9%88%E0%B8%AD-thonglor", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_512230", "name": "Hereduan Street Food (เฮียด่วน) เอกมัย", "cuisine": "Thai", "area": "Ekkamai", "type": "thai", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 31, "newReviews30d": -2617, "velocityPct": -98.8, "tags": ["thai", "ekkamai", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/512230ky-hereduan-street-food-%E0%B9%80%E0%B8%AE%E0%B8%B5%E0%B8%A2%E0%B8%94%E0%B9%88%E0%B8%A7%E0%B8%99-%E0%B9%80%E0%B8%AD%E0%B8%81%E0%B8%A1%E0%B8%B1%E0%B8%A2-ekkamai", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_220226", "name": "Roast theCOMMONS Thonglor", "cuisine": "Cafe", "area": "Thonglor", "type": "cafe", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 136, "newReviews30d": -2636, "velocityPct": -95.1, "tags": ["cafe", "thonglor", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": false, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/roast-thecommons", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_196547Si", "name": "แห้วซีฟู๊ด ปูดองหัวปลาหม้อไฟ พุทธมณฑลสาย 2", "cuisine": "Other", "area": "On Nut", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 0, "newReviews30d": -2679, "velocityPct": -100.0, "tags": ["other", "onnut", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/196547Si-%E0%B9%81%E0%B8%AB%E0%B9%89%E0%B8%A7%E0%B8%8B%E0%B8%B5%E0%B8%9F%E0%B8%B9%E0%B9%8A%E0%B8%94-%E0%B8%9B%E0%B8%B9%E0%B8%94%E0%B8%AD%E0%B8%87%E0%B8%AB%E0%B8%B1%E0%B8%A7%E0%B8%9B%E0%B8%A5%E0%B8%B2%E0%B8%AB%E0%B8%A1%E0%B9%89%E0%B8%AD%E0%B9%84%E0%B8%9F-%E0%B8%9E%E0%B8%B8%E0%B8%97%E0%B8%98%E0%B8%A1%E0%B8%93%E0%B8%91%E0%B8%A5%E0%B8%AA%E0%B8%B2%E0%B8%A2-2", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_367285", "name": "ซูชินะ ฟอร์จูนทาวน์", "cuisine": "Japanese", "area": "Rama 9", "type": "japanese", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 73, "newReviews30d": -2763, "velocityPct": -97.4, "tags": ["japanese", "rama9", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/367285av", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_2703", "name": "พระราม 9 ไก่ย่าง พระราม 9", "cuisine": "Thai", "area": "Rama 9", "type": "thai", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 251, "newReviews30d": -3115, "velocityPct": -92.5, "tags": ["thai", "rama9", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/praram9kaiyang", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_213104", "name": "Holy Shrimp จ๊อดแฟร์แดนเนรมิต", "cuisine": "Other", "area": "Ratchada", "type": "other", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 42, "newReviews30d": -3242, "velocityPct": -98.7, "tags": ["other", "ratchada", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/213104QR-holy-shrimp-jodd-fairs-danneramit", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_2779", "name": "สมบูรณ์โภชนา รัชดา", "cuisine": "Thai", "area": "Ratchada", "type": "thai", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 128, "newReviews30d": -3407, "velocityPct": -96.4, "tags": ["thai", "ratchada", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/somboon-ratchada", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_348033", "name": "เฮียให้ HERE HAI เอกมัย", "cuisine": "Other", "area": "Ekkamai", "type": "other", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 223, "newReviews30d": -3508, "velocityPct": -94.0, "tags": ["other", "ekkamai", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/348033hT-%E0%B9%80%E0%B8%AE%E0%B8%B5%E0%B8%A2%E0%B9%83%E0%B8%AB%E0%B9%89-here-hai-%E0%B9%80%E0%B8%AD%E0%B8%81%E0%B8%A1%E0%B8%B1%E0%B8%A2-ekkamai", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_8476", "name": "ขาหมูเจริญแสงสีลม สีลม", "cuisine": "Other", "area": "Silom", "type": "other", "budget": 1, "budgetLabel": "฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 494, "newReviews30d": -3998, "velocityPct": -89.0, "tags": ["other", "silom", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/chareonsang", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_5720", "name": "วัฒนาพานิช เอกมัย (Ekkamai)", "cuisine": "Other", "area": "Ekkamai", "type": "other", "budget": 2, "budgetLabel": "฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 352, "newReviews30d": -4261, "velocityPct": -92.4, "tags": ["other", "ekkamai", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/wattanapanich", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_135936", "name": "Octave Rooftop Lounge and Bar Bangkok Marriott Hotel Sukhumvit", "cuisine": "Other", "area": "Thonglor", "type": "other", "budget": 4, "budgetLabel": "฿฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 47, "newReviews30d": -5954, "velocityPct": -99.2, "tags": ["other", "thonglor", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/listings/restaurants-in-thonglor#135936", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}, {"id": "wongnai_2097", "name": "ซ้งเป็ดพะโล้ วังหิน", "cuisine": "Other", "area": "Lat Phrao", "type": "other", "budget": 3, "budgetLabel": "฿฿฿", "signalStrength": "weak", "signalCount": 1, "overlapSignal": 1, "trendVelocity": "declining", "trendBadge": "↓ Declining", "totalReviews": 664, "newReviews30d": -5973, "velocityPct": -90.0, "tags": ["other", "ladprao", "wongnai"], "cmNote": "ข้อมูลจาก Wongnai", "isRestaurant": true, "source": "wongnai", "sourceUrl": "https://www.wongnai.com/restaurants/zongpedpalow", "reviewerTiers": {"mega": 0, "macro": 0, "mid": 0}, "lastUpdated": "2026-04-09"}];
