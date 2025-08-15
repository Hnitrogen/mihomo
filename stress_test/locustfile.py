#!/usr/bin/env python3
"""
Clash-Meta Proxy Stress Test using Locust
测试clash-meta在多连接下的性能表现以及瓶颈
"""

import random
import time
import requests
from locust import HttpUser, task, between, events
from locust.env import Environment
import psutil
import threading
import json
import os
from datetime import datetime


class ProxyUser(HttpUser):
    """模拟通过clash-meta代理的用户"""
    
    # 测试目标URL列表 - 随机选择
    # target_urls = [
    #     "https://www.google.com",
    #     "https://httpbin.org/user-agent",
    #     "https://www.github.com",
    #     "https://www.stackoverflow.com",
    #     "https://www.quirkohub.com/ecoflow-ocean-pro-solar-backup-for-efficient-homes/",
    #     "https://nerdbot.com/2025/07/30/enjoy-silent-operation-with-long-lasting-pool-pumps/",
    #     "https://formotorbikes.com/discover-why-electric-trikes-are-safe-for-families/",
    #     "https://www.aaliyahbeautybar.com/post/silk-bedding-deals-this-summer",
    #     "https://whipperberry.com/find-the-right-solar-battery-installers-for-home/",
    #     "https://minimalistfocus.net/why-24-7-support-matters-for-your-pool-vacuum-cleaner/",
    #     "https://www.imei.info/news/m5-ultra-superlight-mouse-perfect-casual-gamers/",
    #     "https://usawire.com/pool-pump-benefits-water-safety-and-easy-refunds/",
    #     "https://ventsmagazine.co.uk/pool-cleaner-using-app-for-easy-maintenance/",
    #     "https://www.bignewsnetwork.com/news/278479630/trusted-robotic-cleaners-artful-pool-safety-solution",
    #     "https://youmotorcycle.com/why-fat-tire-e-bikes-boost-safety-on-rough-terrains.html",
    #     "https://fashionweekonline.com/feel-confident-in-stunning-maxi-and-mini-silk-dresses",
    #     "https://piyarishayari.com/simplify-returns-for-your-electric-pool-pump-needs/",
    #     "https://www.sportalsub.net/en/how-to-install-an-above-ground-pool-pump-efficiently/",
    #     "https://northpennnow.com/news/2025/aug/04/pool-pump-assistance-for-easy-maintenance/",
    #     "https://londonincmagazine.ca/2025/07/19/pool-pumps-for-sale-guide/",
    #     "https://www.elevatedmagazines.com/single-post/what-s-covered-in-igarden-s-pool-motor-pump-warranty",
    #     "https://industrywired.com/lifestyle/avoid-mistakes-in-above-ground-pool-pump-purchases-and-shipping-9616069",
    #     "https://www.buddymagazine.org/business/how-do-you-prime-a-pool-pump-with-fast-delivery",
    #     "https://www.bizzbuzz.news/LifeStyle/guide-to-selecting-pool-pumps-with-warranty-coverage-1368829",
    #     "https://childrensbooksdaily.com/avoid-pool-pump-failures-with-expert-repair-support/",
    #     "https://adventuresfrugalmom.com/why-choose-quiet-and-efficient-pool-cover-pumps/",
    #     "https://tradebrains.in/brand/innovative-pool-vacuum-robots-professional-cleaning-trends/",
    #     "https://www.verticalwise.com/automatic-pool-vacuum-essentials-for-homeowners/",
    #     "https://www.sippycupmom.com/avoid-pool-cleaning-hassles-with-smart-customer-support/",
    #     "https://theenterpriseworld.com/robotic-pool-cleaners/",
    #     "https://londonlovesbusiness.com/effortless-pool-maintenance-with-reliable-wireless-cleaner-support/",        
    #     "https://www.adorecharlotte.co.uk/hassle-free-auto-pool-cleaner-returns-and-replacements/",
    #     "https://thecoastline-magazine.com/master-ai-features-in-robotic-pool-cleaners-guide/",
    #     "https://momwifewine.com/2025/08/01/traditional-cleaning-vs-ai-pool-cleaners-which-wins/",
    #     "https://www.imei.info/news/how-implement-advanced-robot-vacuums-pool-maintenance/",
    #     "https://www.flushthefashion.com/culture/is-igarden-the-quietest-energy-efficient-above-ground-pool-pump/",   
    #     "https://famousparenting.com/how-to-optimize-hypercar-inspired-pool-vacuum-robots/",
    #     "https://www.mothersalwaysright.com/effortless-lawn-care-with-ai-driven-cleaning-tech/",
    #     "https://medicalresearch.com/innovative-dental-solutions-for-enhanced-clinic-comfort/",
    #     "https://motherhood.com.sg/education/optimize-pool-pump-settings/",
    #     "https://www.openpr.com/news/4130943/what-to-know-about-electric-pool-pump-warranties",
    #     "https://smartsimregistration.net/safe-above-ground-pool-pump-operation/",
    #     "https://www.onyamagazine.com/australian-affairs/need-24-7-support-for-pool-pumps-find-out-how/",
    #     "https://gingerparrot.co.uk/pags/reliable-pool-pump-maintenance-solutions-for-homeowners.html",
    #     "https://speedwaymedia.com/2025/08/05/compare-energy-efficient-vs-standard-pool-pumps-now/",
    #     "https://www.budgetsavvydiva.com/2025/08/touch-screen-pool-motor-pump-modern-control-for-smart-homes/",       
    #     "https://programminginsider.com/how-to-access-pool-pump-customer-assistance/",
    #     "https://urbanasian.com/lifestyle/2025/08/are-you-maintaining-your-pool-pump-covers-correctly/",
    #     "https://kharadipune.com/save-energy-with-advanced-dental-lighting-solutions/",
    #     "https://gretasjunkyard.com/how-do-you-prime-a-pool-pump-for-both-pools-and-hot-tubs/",
    #     "https://theprothots.com/why-choose-digital-x-ray-equipment-for-dental-safety/",
    #     "https://emedicodiary.com/post/1351/how-to-identify-top-dental-air-compressor-suppliers",
    #     "https://www.primaryonehealth.org/wp-content/pgs/?essential-guide-to-hygienic-dental-tool-organization-systems.html",
    #     "https://yourhealthmagazine.net/article/practice-management/why-choose-ergonomic-dental-chairs-for-patient-comfort/",
    #     "https://www.healthlabspartners.com/guide-to-enhancing-efficiency-with-quality-dental-components.html",
    #     "https://doctorspot.in/health/expert-dental-chairs-for-sale-climate-adaptive-solutions-worldwide/",
    #     "https://www.healthbloomin.com/expert-trends-in-high-capacity-dental-chair-parts/",
    #     "https://dentaltown.com/blog/post/23208/how-to-choose-chairs-with-sensor-activated-led-safety",
    #     "https://theinscribermag.com/how-to-choose-a-quiet-operation-pool-cover-pump/",
    #     "https://michiganmamanews.com/2025/08/04/how-to-achieve-hassle-free-pool-maintenance-with-robot-vacuums/",
    #     "https://www.digitaljournal.com/pr/news/binary-news-network/pool-cleaner-smart-enough-future-1241248206.html",
    #     "https://widebaykids.com.au/expert-insights-on-heavy-debris-suction-in-modern-pool-vacuums/",
    #     "https://thehometrotters.org/how-robotic-cleaners-enhance-smart-filtration-efficiency/",
    #     "https://stylevanity.com/2025/08/how-to-optimize-flow-system-in-your-wireless-pool-cleaner.html",
    #     "https://lifestylebyps.com/blogs/the-design-blog/essential-pool-drain-pump-maintenance-guide",
    #     "https://www.latestly.com/lifestyle/superior-pool-cleaners-vs-heavy-debris-why-they-prevail-7044230.html",
    #     "https://www.theglobeandmail.com/investing/markets/markets-news/GetNews/33893920/mvraki-unveils-bold-new-line-of-labgrown-diamond-statement-rings/",
    #     "https://timeshealthmag.com/sparkle-consciously-with-lab-grown-diamond-earrings/",
    #     "https://londonincmagazine.ca/2025/07/20/radiant-lab-grown-colored-diamonds/",
    #     "https://tradebrains.in/brand/unlock-fast-delivery-for-allen-bradley-control-parts/",
    #     "https://www.theglobeandmail.com/investing/markets/markets-news/GetNews/33893632/rabwellplc-offers-allen-bradley-plc-control-systems-at-unbeatable-prices-with-rapid-shipping/",
    #     "https://northpennnow.com/news/2025/aug/04/avoid-overspending-on-affordable-siemens-plc-components/",
    #     "https://techbullion.com/how-to-save-on-schneider-plc-shipping-with-dhl-and-ups/",
    #     "https://www.buddymagazine.org/tech/beckhoff-plc-support-for-system-integrators-needs",
    #     "https://www.bizzbuzz.news/industry/energy/abb-drives-expert-warranty-and-shipping-insights-1368873",
    #     "https://elperiodicodeyecla.com/schneider-plc-controller/",
    #     "https://www.gudstory.com/maximizing-solar-battery-life-with-thermal-insulation-tips/",
    #     "https://www.universitymagazine.ca/portable-power-stations-reliable-outdoor-energy-gear/",
    #     "https://greenbuildingcanada.ca/portable-power-stations-emergency-power/",
    #     "https://www.intelligenthq.com/a-guide-to-crafting-custom-sounds-via-text-to-audio-ai/",
    #     "https://www.designviva.com/can-flood-resistant-solar-systems-secure-your-home-energy/",
    #     "https://myflashyhome.com/leading-trends-in-home-solar-the-rise-of-smart-energy-storage/",
    #     "https://rafaria.com/how-to-size-solar-batteries-for-high-wattage-appliances/",
    #     "https://propertycostarica.co.uk/how-to-integrate-fast-charging-for-smart-home-circuits/",
    #     "https://lookwhatmomfound.org/reliable-home-battery-backup-for-uninterrupted-home-power/",
    #     "https://f95zoneus.net/climate-affects-your-home-solar-storage-performance/",
    #     "https://theceoviews.com/are-solar-panels-your-energy-saving-answer/",
    #     "https://www.ilounge.com/articles/compact-power-station-solutions-for-outdoor-enthusiasts",
    #     "https://mydecine.com/unlock-freedom-with-reliable-portable-power-stations-for-camping/",
    #     "https://newsprovider.co.uk/how-can-solar-generators-provide-true-energy-independence/",
    #     "https://techbullion.com/how-to-choose-the-best-power-station-for-emergencies/",
    #     "https://baddiehub.ca/guide-to-joining-ecocredits-for-eco-friendly-power-station-deals/",
    #     "https://www.re-thinkingthefuture.com/technologies/gp5396-maximize-pool-energy-efficiency-with-smart-water-pump-control/",
    #     "https://metapress.com/electric-pool-pumps-boost-performance-with-durable-motors/",
    #     "https://anationofmoms.com/2025/07/above-ground-pool-pumps.html",
    #     "https://www.harlemworldmagazine.com/sponsored-love-avoid-common-mistakes-in-swimming-pool-pump-installation/",
    #     "https://techbullion.com/quiet-eco-pumps-outperform-noisy-models/",
    #     "https://www.abcmoney.co.uk/2025/07/pool-maintenance-made-easy-24-7-help-now-available-for-pump-cover-use/",
    #     "https://northeast.newschannelnebraska.com/story/52954374/step-by-step-guide-to-priming-your-pool-pump-efficiently",
    #     "https://guruhitech.com/boost-your-pumps-lifespan-with-proper-equipment-positioning/",
    #     "https://emedicodiary.com/post/1332/is-your-pool-pump-costing-too-much-repair-solutions",
    #     "https://enthrallinggumption.com/prevent-pool-cover-pump-failure-with-expert-care/",
    #     "https://www.theyeshivaworld.com/news/general/2430967/pool-vacuum-robots-smart-automatic-cleaning-solutions.html",
    #     "https://www.netnewsledger.com/2025/07/28/advanced-automatic-pool-cleaner-vacuum-efficiency-guide/",
    #     "https://www.momooze.com/struggling-with-wireless-pool-cleaner-returns-get-support/",
    #     "https://brightsideofnews.com/lifestyle/auto-pool-cleaner-warranty-protect-your-investment-effortlessly/",
    #     "https://researchsnipers.com/automatic-pool-cleaners-for-family-safety-and-spotless-water/",
    #     "https://ventsmagazine.com/2025/07/27/why-is-your-inground-pool-water-cloudy-vacuum-solutions/",
    #     "https://techbehindit.com/gadgets/how-to-maintain-sparkling-pool-water-with-robotic-cleaners/",
    #     "https://teamgroupname.com/achieve-crystal-clear-water-with-ai-driven-pool-cleaners/",
    #     "https://www.techloy.com/is-your-pool-pump-safe-from-dry-running/",
    #     "https://cordless.io/above-ground-pool-pump-shipping-what-to-expect/",
    #     "https://greenrecord.co.uk/avoid-common-pitfalls-in-pool-vacuum-robot-shipping/",
    #     "https://formotorbikes.org/is-full-suspension-ebike-the-key-to-faster-commuting/",
    #     "https://fashionisks.com/why-choose-silk-underwear-for-breathable-comfort/",
    #     "https://www.political.fashion/posts/why-silk-nightgowns-define-ultimate-luxury-sleepwear",
    #     "https://www.fashionabc.org/luxurious-silk-robes-for-her-special-moments/",
    #     "https://www.fashionlobby.ca/indulge-in-elegant-ladies-silk-sleepwear-now",
    #     "https://techbullion.com/secure-payment-tips-for-new-40-inch-tv-shoppers/",
    #     "https://dunkin-donut.net/master-energy-management-using-smart-visualization-technology/",
    #     "https://designrelated.com/ecoflow-ocean-pros-led-display-inverter/",
    #     "https://www.spiritedpuddlejumper.com/sustainable-energy-solutions-for-modern-homes/",
    #     "https://www.re-thinkingthefuture.com/technologies/gp5294-can-ocean-pro-solar-battery-secure-your-home-power/",
    #     "https://www.hudsonfarmhouse.com/how-to-secure-your-home-with-solar-energy-systems/",
    #     "https://thehometrotters.org/solar-energy-management/",
    #     "https://livepositively.com/boost-your-business-with-solar-certification-training-solutions/",
    #     "https://ahouseinthehills.com/master-home-energy-management-with-smart-solar-solutions/",
    #     "https://optimisticmommy.com/power-your-home-independently-with-diy-solar-storage/",
    #     "https://avstarnews.com/is-a-home-battery-your-ultimate-backup-power-solution/",
    #     "https://www.uvig.org/can-ocean-pro-solar-battery-slash-your-energy-bills/",
    #     "https://goodmenproject.com/everyday-life-2/master-backup-power-using-ocean-pro-and-ecoflow-app/",
    #     "https://homebriefings.com/home-battery-backup-revolutionize/",
    #     "https://azbigmedia.com/business/arizona-energy-industry/cut-energy-bills-with-home-battery-efficiency/",
    #     "https://enthrallinggumption.com/protect-solar-investments-from-extreme-weather-risks/",
    #     "https://intheplayroom.co.uk/maximize-solar-energy-for-home-smart-storage-solutions/",
    #     "https://hunkwhiz.com/maximize-energy-savings-with-the-right-solar-battery-integration/",
    #     "https://rizzlineshub.com/ocean-pro-your-smart-solution-for-eco-friendly-energy/",
    #     "https://gluesticksgumdrops.com/9-things-you-can-do-now-to-prepare-for-a-power-outage/",
    #     "https://thedesigntourist.com/is-your-home-ready-for-solar-energy-and-battery-storage/",
    #     "https://www.thecuriouslycreative.com/avoid-charging-mistakes-with-home-solar-batteries-outdoors/",
    #     "https://www.revoada.net/maximize-savings-with-solar-power-and-tax-credits/",
    #     "https://resident.com/resource-guide/2025/07/22/are-your-solar-installations-safe-and-compliant-for-rentals",
    #     "https://americanspcc.org/ocean-pro-home-battery-ultimate-energy-tracking-guide/",
    #     "https://www.thepinnaclelist.com/articles/maximizing-home-solar-energy-with-smart-tech/",
    #     "https://dgmnews.com/posts/can-ai-sound-effects-revolutionize-your-marketing-strategy/",
    #     "https://tygiadola.net/unlock-freedom-solar-generators-for-ultimate-camping-power/",
    #     "https://thehometrotters.com/how-to-select-portable-power-stations-with-maximum-storage-capacity/",
    #     "https://amazingarchitecture.com/articles/solar-generator-solutions-for-efficient-power-outages",
    #     "https://www.mothersalwaysright.com/is-a-portable-power-station-your-ideal-home-backup-solution/",
    #     "https://officepoolstop.com/blog/maximize-ecocredits-smart-energy-storage-devices",
    #     "https://omnisizes.com/home-decor/how-inverter-generators-provide-quiet-off-grid-power-solutions/",
    #     "https://www.entrepreneurshiplife.com/portable-power-station-backup-solutions-for-homeowners/",
    #     "https://www.mynewsgh.com/need-reliable-backup-power-try-portable-solar-generators/",
    #     "https://grobuzz.co.uk/unleash-adventure-with-solar-power-stations-on-the-go/",
    #     "https://infotopbio.com/2025/07/18/power-your-adventures-with-lightweight-solar-generators/",
    #     "https://dimensionsscript.com/can-solar-panels-cut-your-home-energy-bills/",
    #     "https://ocnjdaily.com/news/2025/jul/23/how-to-use-solar-power-off-grid/",
    #     "https://snoozye.com/how-to-know-if-your-inverter-generator-solar-ready-for-camping-adventures/",
    #     "https://www.starleaf.com/blog/expert-guide-to-solar-panel-capacity-and-efficiency/",
    #     "https://blessingbeam.com/portable-power-stations-eco-conscious-solutions-for-savings/",
    #     "https://breakingac.com/news/2025/jul/21/ensure-continuous-work-with-desktop-power/",
    #     "https://www.upbeatgeek.com/elevate-games-with-ai-music-creator-tools/",
    #     "https://hacker9.com/how-does-kling-ai-transform-your-video-sound-effects/",
    #     "https://fontsarena.com/blog/can-ai-sound-effects-revolutionize-marketing-visuals/",
    #     "https://thecoastline-magazine.com/how-to-apply-ai-generators-for-professional-image-enhancement/",
    #     "https://thehake.com/2025/07/can-ai-sound-effects-revolutionize-graphic-design-workflow/",
    #     "https://www.opensourcefeed.org/insights/ai-image-generator-design-workflow/",
    #     "https://illustrarch.com/artificial-intelligence/54307-unlock-fast-professional-image-creation-with-ai-sound-effects.html",
    #     "https://pixelixe.com/blog/can-ai-sound-effects-revolutionize-your-visual-marketing/",
    #     "https://azbigmedia.com/business/arizona-energy-industry/can-home-solar-systems-slash-your-carbon-footprint/",
    #     "https://www.theenvironmentalblog.org/2025/07/avoiding-overpriced-battery-solutions-for-solar-contractors/",
    #     "https://ventsmagazine.co.uk/advanced-tips-for-optimizing-solar-panel-efficiency/",
    #     "https://techbullion.com/avoid-legal-risks-in-diy-solar-solutions-for-your-home/",
    #     "https://techktimes.co.uk/how-to-integrate-home-solar-with-smart-home-tech/",
    #     "https://2amagazine.com/ecoflow-delta-pro-ultra-ultimate-home-solar-solution/",
    #     "https://resident.com/resource-guide/2025/07/24/is-ecoflow-stream-compatible-with-home-solar-systems",
    #     "https://www.re-thinkingthefuture.com/technologies/gp5304-microinverters-vs-string-inverters-the-ultimate-home-solar-choice/",
    #     "https://metapress.com/how-can-homeowners-save-with-home-solar-systems/",
    #     "https://www.urbansplatter.com/2025/07/revolutionize-home-ev-charging-with-solar-integration/",
    #     "https://www.raysfixly.com/portable-power-stations-for-secure-home-office-energy/",
    #     "https://www.re-thinkingthefuture.com/technologies/gp5343-essential-guide-to-gaming-mouse-durability-and-comfort/",
    #     "https://www.theglobeandmail.com/investing/markets/markets-news/GetNews/33570142/mambasnake-simplifies-wireless-gaming-mouse-experience-with-easy-driver-software-setup/",
    #     "https://coruzant.com/tech/mechanical-keyboard-maintenance-tips/",
    #     "https://www.barchart.com/story/news/33570208/mambasnake-unveils-custom-keyboard-solutions-to-boost-gaming-precision-and-comfort",
    #     "https://tradebrains.in/brand/feel-the-difference-customizable-rapid-trigger-keyboards-that-excite/",
    #     "https://nerdbot.com/2025/07/23/enhance-home-decor-with-frameless-smart-tvs/",
    #     "https://sosomodapks.com/how-to-set-up-dolby-hdr-on-your-55-inch-smart-tv/",
    #     "https://usawire.com/how-to-set-up-credit-alerts-for-limit-safety/",
    #     "https://iasdetails.com/boost-engagement-using-ai-sound-effects-and-visual-tools/",
    #     "https://skyryedesign.com/architecture/home/how-to-profit-from-home-solar-energy-with-virtual-power-plants/",
    #     "https://meaningsinlife.com/why-every-home-needs-a-power-station-for-emergencies/",
    #     "https://techprimex.com/secure-kids-items-sound-alarms-boost-tracking-accuracy/",
    #     "https://speromagazine.com/master-ai-sound-effects-for-better-video-ads/",
    #     "https://learn.nctsn.org/tag/index.php?tc=1&tag=find-relief-with-mindful-adhd",
    #     "https://inhaltwelt.de/warum-grose-kuhlbettdecken-fur-nachtschweis-wahlen/",
    #     "https://northpennnow.com/news/2025/jul/03/how-can-portable-power-stations-enhance-your-outdoor-adventures/",
    #     "https://siliconvalleytime.com/article/unlock-solar-savings-and-tax-credits-today/",
    #     "https://floridahottopics.com/avoid-solar-generator-pitfalls-for-safe-energy-storage/",
    #     "https://gimkitjoin.net/is-your-home-prepared-for-power-outages/",
    #     "https://wordstreetjournal.com/solar-generators-your-path-to-renewable-energy-freedom/",
    #     "https://inglishe.com/calculate-solar-panels-required-by-your-energy-consumption/",
    #     "https://www.thecuriouslycreative.com/secure-your-work-reliable-portable-power-solutions/",
    #     "https://wishhes.com/silent-power-solutions-for-your-home-electronics/",
    #     "https://cordless.io/monocrystalline-vs-polycrystalline-solar-panel-comparison/",
    #     "https://usawire.com/portable-power-solutions-for-camping-reliability/",
    #     "https://dsnews.co.uk/how-to-choose-the-ideal-medium-capacity-solar-generator/",
    #     "https://theartisticmind.com/unlock-rv-power-with-foldable-solar-panel-benefits/",
    #     "https://www.kulfiy.com/solar-generators-sustainable-energy-solutions-for-eco-homes/",
    #     "https://resident.com/resource-guide/2025/07/08/unlock-maximum-roi-with-solar-panels-for-investors",
    #     "https://stringlabscreative.com/why-choose-inverter-generators-for-maintenance-free-operation/",
    #     "https://thecollectivenouns.com/whats-the-best-portable-power-station-for-camping/",
    #     "https://azbigmedia.com/business/innovative-solutions-for-expanding-your-arizona-based-business/",
    #     "https://livenewschat.eu/are-hybrid-inverter-generators-safer-for-homes/",
    #     "https://masonjarbreakfast.com/ecoflow-river-3-safe-power-for-essential-devices/",
    #     "https://toolyatri.com/portable-solar-power-solutions-for-effortless-road-trip-charging/",
    #     "https://bsglife.com/maximize-home-energy-savings-with-solar-panel-solutions/",
    #     "https://propertycostarica.co.uk/how-to-choose-a-solar-generator-for-home-outages/",
    #     "https://amourvert.com/articles/how-to-secure-energy-with-ecoflow-delta-charging",
    #     "https://englishsumup.com/power-your-camping-adventures-with-reliable-portable-stations/",
    #     "https://minimalistfocus.net/monocrystalline-vs-polycrystalline-solar-panel-showdown/",
    #     "https://autism.fm/avoid-power-shortages-with-solar-generators-while-camping/",
    #     "https://industrywired.com/tech/how-to-use-a-portable-power-station-for-reliable-home-backup-9469618",
    #     "https://www.psychologs.com/feel-empowered-with-solar-panel-independence/",
    #     "https://www.smiletotalk.com/blog/slash-electricity-bills-with-solar-generator-backup",
    #     "https://www.wispwillow.com/tech/portable-power-for-camping/",
    #     "https://insightsjournal.co.uk/set-up-a-portable-power-station-for-home-backup/",
    #     "https://www.toocoolwebs.com/how-to-install-solar-panels-for-optimal-energy-generation/",
    #     "https://aajkitajikhabar.com/how-do-solar-generators-ensure-reliable-home-backup/",
    #     "https://startup.info/how-to-choose-the-best-portable-power-for-camping/",
    #     "https://glowtechy.com/camping-power-made-quiet-with-inverter-generators/",
    #     "https://www.readability.com/how-to-select-compact-power-stations-for-travel/",
    #     "https://thetundradrums.com/solar-generators-x-boost-technology/",
    #     "https://www.emailsettingspot.com/inverter-generators-vs-conventional-fuel-savings-guide/",
    #     "https://dessertscapital.com/avoid-common-pitfalls-when-selecting-a-home-power-station/",
    #     "https://www.greencitytimes.com/ecoflow-delta-2/",
    #     "https://applebemenu.com/solar-generator-benefits-for-safe-eco-friendly-power/",
    #     "https://logisticsuk.org/guide-to-compact-backup-power-stations/",
    #     "https://www.buddymagazine.org/tech/how-to-choose-fuel-efficient-power-for-outdoor-excursions",
    #     "https://nomefy.com/reduce-home-energy-costs-with-solar-panels-now/",
    #     "https://gingerparrot.co.uk/pags/the-evolution-of-home-power-backup-solutions.html",
    #     "https://www.re-thinkingthefuture.com/technologies/gp5202-fat-tire-vs-standard-e-bikes-off-road-dominance/",
    #     "https://techoelite.com/how-electric-bikes-solve-busy-commuter-storage/",
    #     "https://www.home-dzine.co.za/Lifestyle/offroad-e-bikes-conquer-trails-with-lasting-warranty.html",
    #     "https://blogbuz.co.uk/feel-excitement-with-essential-e-bike-accessories/",
    #     "https://michiganmamanews.com/2025/07/08/why-choose-a-fat-tire-ebike-for-fast-urban-commuting/",
    #     "https://flyarchitecture.net/2025/07/09/guide-to-choosing-your-perfect-commuter-ebike-for-safety/",
    #     "https://minimalistfocus.net/durable-off-road-e-bikes-for-riders/",
    #     "https://indianautosblog.com/best-rated-electric-bikes-safe-and-efficient-urban-transport-p327722",
    #     "https://formotorbikes.com/avoid-discomfort-fat-tire-e-bike-tips-for-rough-terrains/",
    #     "https://www.mangalorean.com/author/Holistic-ADHD-Treatment-Options-in-Richmond-Hill/",
    #     "https://techbullion.com/unleash-your-adventure-with-tactical-backpacks/",
    #     "https://mikromart.com/anti-bend-ipad-11th-gen-case-for-safe-sketching-needs/",
    #     "https://davidsbeenhere.com/2025/07/11/unlock-energy-independence-through-optimal-sunlight-use/",
    #     "https://homethreads.org/safe-and-fast-camping-power-ecoflow-river-3-plus-power-station/",
    #     "https://www.revoada.net/save-money-with-budget-solar-panels/",
    #     "https://www.mindmybusinessnyc.com/avoid-these-mistakes-portable-e-bike/",
    #     "https://www.re-thinkingthefuture.com/technologies/gp5218-secure-your-gear-sport-shooters-essential-gun-case-guide/",
    #     "https://www.theglobeandmail.com/investing/markets/markets-news/GetNews/33360123/dulcedom-introduces-waterresistant-range-bags-designed-for-tactical-gear-protection",
    #     "https://tradebrains.in/brand/durable-hunting-backpacks-for-outdoor-gear-protection/",
    #     "https://ventsmagazine.co.uk/online-adhd-consultation-enhance-personalized-care/",
    #     "https://dimensionsscript.com/how-do-mental-health-platforms-handle-online-adderall-prescriptions/",
    #     "https://penzu.com/p/cfd27c858b58862c",
    #     "https://wakelet.com/wake/7Xwjz5Tqw3hmsv1gjXaVc",
    #     "https://grammerheist.com/can-you-access-affordable-adhd-care-online/",
    #     "https://infowebs.de/5-zubehor-empfehlungen-fur-dein-iphone-die-deinen-alltag-spurbar-smarter-machen",
    #     "https://beitraghub.de/iphone-life-hacks-5-gadgets-die-dein-iphone-wirklich-smarter-machen/",
    #     "https://entrepreneursbreak.de/everyday-iphone-essentials-5-zubehorteile-die-deinen-alltag-wirklich-erleichtern/",
    #     "https://www.urbansplatter.com/2025/07/empower-your-home-with-eco-friendly-solar-solutions-maximizing-efficiency-and-savings/",
    #     "https://idighardware.com/author/canfloodresist/",
    #     "https://anationofmoms.com/2025/07/solar-power-for-your-home.html",
    #     "https://thecollectivenouns.com/achieve-energy-independence-with-whole-home-battery-backup/",
    #     "https://adventuresfrugalmom.com/is-solar-battery-storage-right-for-your-home-power-needs/",
    #     "https://www.amountainmomma.com/how-to-maximize-backup-with-ecoflow-ocean-pro-ai-mode/",
    #     "https://ymovieshd.org/expert-guide-to-portable-solar-power-for-campers/",
    #     "https://feedbuzzard.com/maximize-your-power-station-benefits-with-ecoflow-membership/",
    #     "https://disquantified.org/how-to-save-money-with-solar-panels-a-budget-conscious-guide/",
    #     "https://scientificasia.net/how-ecoflows-power-station-loyalty-program-saves-you-more/",
    #     "https://monomousumi.com/reliable-home-backup-power-with-solar-charging-solutions/",
    #     "https://icilome.com/2025/06/laveuse-de-bouteilles-pour-alimentation-des-nourrissons/",
    #     "https://speromagazine.com/home-solar-system-ecoflow-stream-ultra-for-portable-energy-savings/",
    #     "https://www.urbansplatter.com/2025/06/solar-battery-backup-solutions-for-energy-savings/",
    #     "https://www.portotheme.com/how-to-integrate-ecoflow-delta-pro-ultra-with-rooftop-solar/",
    #     "https://houseofcoco.net/how-to-enhance-grid-tied-solar-with-battery-backup-solutions/",
    #     "https://www.aquionenergy.com/avoid-energy-waste-in-home-solar/",
    #     "https://techbullion.com/clou-ess-showed-up-at-re-boosting-industry-revenue-with-entire-lifecycle-service/",
    #     "https://www.uktech.news/other_news/clou-ess-makes-an-entrance-at-re-enhancing-sector-revenue-through-comprehensive-lifecycle-services",
    #     "https://techbar.org/the-essential-guide-to-electric-skateboard-maintenance/",
    #     "https://blogbuz.co.uk/how-can-a-modern-power-station-transform-your-energy-efficiency/",
    #     "https://www.healthcarter.com/en-us/education/how-to-choose-the-best-portable-power-station-for-reliable-home-backup-power/",
    #     "https://londonincmagazine.ca/2025/05/01/solar-generators-for-homes/",
    #     "https://timeshealthmag.com/solar-generators-achieving-energy-independence-sustainably/",
    #     "https://durostech.com/how-to-choose-the-perfect-portable-power-station-for-your-needs/",
    #     "https://www.theglobeandmail.com/investing/markets/markets-news/GetNews/32575139/urtopia-champions-simplicity-with-its-elegant-city-e-bike-for-modern-commuters/",
    #     "https://www.thebikerguide.co.uk/motorcyclenews/read_207551/why-are-folding-electric-cycles-transforming-urban-commuting.html",
    #     "https://www.outdoorproject.com/users/discover-how-urban-ebikes-can-transform-your-daily-commute",
    #     "https://techbullion.com/discover-the-lightest-electric-bicycle-for-effortless-adventures/",
    #     "https://www.barchart.com/story/news/32560623/explore-premium-fat-tire-electric-bikes-for-high-performance-cycling",
    #     "https://www.therarewelshbit.com/5-ways-hotels-can-be-more-eco-friendly/",
    #     "https://celebstowiki.com/how-to-find-ipad-cases-supporting-creative-functionality/",
    #     "https://ultimatestatusbar.com/why-pick-a-detachable-keyboard-case-for-ipad/",
    #     "https://williamkamkwamba.com/set-up-microinverter-solar-kit/",
    #     "https://www.theglobeandmail.com/investing/markets/markets-news/GetNews/33360123/dulcedom-introduces-waterresistant-range-bags-designed-for-tactical-gear-protection",
    #     "https://tradebrains.in/brand/durable-hunting-backpacks-for-outdoor-gear-protection/",
    #     "https://ventsmagazine.co.uk/online-adhd-consultation-enhance-personalized-care/",
    #     "https://dimensionsscript.com/how-do-mental-health-platforms-handle-online-adderall-prescriptions/",
    #     "https://penzu.com/p/cfd27c858b58862c",
    #     "https://wakelet.com/wake/7Xwjz5Tqw3hmsv1gjXaVc",
    #     "https://grammerheist.com/can-you-access-affordable-adhd-care-online/",
    #     "https://infowebs.de/5-zubehor-empfehlungen-fur-dein-iphone-die-deinen-alltag-spurbar-smarter-machen",
    #     "https://beitraghub.de/iphone-life-hacks-5-gadgets-die-dein-iphone-wirklich-smarter-machen/",
    #     "https://entrepreneursbreak.de/everyday-iphone-essentials-5-zubehorteile-die-deinen-alltag-wirklich-erleichtern/",
    #     "https://www.urbansplatter.com/2025/07/empower-your-home-with-eco-friendly-solar-solutions-maximizing-efficiency-and-savings/",
    #     "https://idighardware.com/author/canfloodresist/",
    #     "https://anationofmoms.com/2025/07/solar-power-for-your-home.html",
    #     "https://thecollectivenouns.com/achieve-energy-independence-with-whole-home-battery-backup/",
    #     "https://adventuresfrugalmom.com/is-solar-battery-storage-right-for-your-home-power-needs/",
    #     "https://www.amountainmomma.com/how-to-maximize-backup-with-ecoflow-ocean-pro-ai-mode/",
    #     "https://ymovieshd.org/expert-guide-to-portable-solar-power-for-campers/",
    #     "https://feedbuzzard.com/maximize-your-power-station-benefits-with-ecoflow-membership/",
    #     "https://disquantified.org/how-to-save-money-with-solar-panels-a-budget-conscious-guide/",
    #     "https://scientificasia.net/how-ecoflows-power-station-loyalty-program-saves-you-more/",
    #     "https://monomousumi.com/reliable-home-backup-power-with-solar-charging-solutions/",
    #     "https://icilome.com/2025/06/laveuse-de-bouteilles-pour-alimentation-des-nourrissons/",
    #     "https://speromagazine.com/home-solar-system-ecoflow-stream-ultra-for-portable-energy-savings/",
    #     "https://www.urbansplatter.com/2025/06/solar-battery-backup-solutions-for-energy-savings/",
    #     "https://www.portotheme.com/how-to-integrate-ecoflow-delta-pro-ultra-with-rooftop-solar/",
    #     "https://houseofcoco.net/how-to-enhance-grid-tied-solar-with-battery-backup-solutions/",
    #     "https://www.aquionenergy.com/avoid-energy-waste-in-home-solar/",
    #     "https://techbullion.com/clou-ess-showed-up-at-re-boosting-industry-revenue-with-entire-lifecycle-service/",
    #     "https://www.uktech.news/other_news/clou-ess-makes-an-entrance-at-re-enhancing-sector-revenue-through-comprehensive-lifecycle-services",
    #     "https://techbar.org/the-essential-guide-to-electric-skateboard-maintenance/",
    #     "https://blogbuz.co.uk/how-can-a-modern-power-station-transform-your-energy-efficiency/",
    #     "https://www.healthcarter.com/en-us/education/how-to-choose-the-best-portable-power-station-for-reliable-home-backup-power/",
    #     "https://londonincmagazine.ca/2025/05/01/solar-generators-for-homes/",
    #     "https://timeshealthmag.com/solar-generators-achieving-energy-independence-sustainably/",
    #     "https://durostech.com/how-to-choose-the-perfect-portable-power-station-for-your-needs/",
    #     "https://www.theglobeandmail.com/investing/markets/markets-news/GetNews/32575139/urtopia-champions-simplicity-with-its-elegant-city-e-bike-for-modern-commuters/",
    #     "https://www.thebikerguide.co.uk/motorcyclenews/read_207551/why-are-folding-electric-cycles-transforming-urban-commuting.html",
    #     "https://www.outdoorproject.com/users/discover-how-urban-ebikes-can-transform-your-daily-commute",
    #     "https://techbullion.com/discover-the-lightest-electric-bicycle-for-effortless-adventures/",
    #     "https://www.barchart.com/story/news/32560623/explore-premium-fat-tire-electric-bikes-for-high-performance-cycling",
    #     "https://www.therarewelshbit.com/5-ways-hotels-can-be-more-eco-friendly/",
    #     "https://celebstowiki.com/how-to-find-ipad-cases-supporting-creative-functionality/",
    #     "https://ultimatestatusbar.com/why-pick-a-detachable-keyboard-case-for-ipad/",
    #     "https://williamkamkwamba.com/set-up-microinverter-solar-kit/",
    #     "https://ventsmagazine.co.uk/online-adhd-consultation-enhance-personalized-care/",
    #     "https://dimensionsscript.com/how-do-mental-health-platforms-handle-online-adderall-prescriptions/",
    #     "https://penzu.com/p/cfd27c858b58862c",
    #     "https://wakelet.com/wake/7Xwjz5Tqw3hmsv1gjXaVc",
    #     "https://grammerheist.com/can-you-access-affordable-adhd-care-online/",
    #     "https://infowebs.de/5-zubehor-empfehlungen-fur-dein-iphone-die-deinen-alltag-spurbar-smarter-machen",
    #     "https://beitraghub.de/iphone-life-hacks-5-gadgets-die-dein-iphone-wirklich-smarter-machen/",
    #     "https://entrepreneursbreak.de/everyday-iphone-essentials-5-zubehorteile-die-deinen-alltag-wirklich-erleichtern/",
    #     "https://www.urbansplatter.com/2025/07/empower-your-home-with-eco-friendly-solar-solutions-maximizing-efficiency-and-savings/",
    #     "https://idighardware.com/author/canfloodresist/",
    #     "https://anationofmoms.com/2025/07/solar-power-for-your-home.html",
    #     "https://thecollectivenouns.com/achieve-energy-independence-with-whole-home-battery-backup/",
    #     "https://adventuresfrugalmom.com/is-solar-battery-storage-right-for-your-home-power-needs/",
    #     "https://www.amountainmomma.com/how-to-maximize-backup-with-ecoflow-ocean-pro-ai-mode/",
    #     "https://ymovieshd.org/expert-guide-to-portable-solar-power-for-campers/",
    #     "https://feedbuzzard.com/maximize-your-power-station-benefits-with-ecoflow-membership/",
    #     "https://disquantified.org/how-to-save-money-with-solar-panels-a-budget-conscious-guide/",
    #     "https://scientificasia.net/how-ecoflows-power-station-loyalty-program-saves-you-more/",
    #     "https://monomousumi.com/reliable-home-backup-power-with-solar-charging-solutions/",
    #     "https://icilome.com/2025/06/laveuse-de-bouteilles-pour-alimentation-des-nourrissons/",
    #     "https://speromagazine.com/home-solar-system-ecoflow-stream-ultra-for-portable-energy-savings/",
    #     "https://www.urbansplatter.com/2025/06/solar-battery-backup-solutions-for-energy-savings/",
    #     "https://www.portotheme.com/how-to-integrate-ecoflow-delta-pro-ultra-with-rooftop-solar/",
    #     "https://houseofcoco.net/how-to-enhance-grid-tied-solar-with-battery-backup-solutions/",
    #     "https://www.aquionenergy.com/avoid-energy-waste-in-home-solar/",
    #     "https://techbullion.com/clou-ess-showed-up-at-re-boosting-industry-revenue-with-entire-lifecycle-service/",
    #     "https://www.uktech.news/other_news/clou-ess-makes-an-entrance-at-re-enhancing-sector-revenue-through-comprehensive-lifecycle-services",
    #     "https://techbar.org/the-essential-guide-to-electric-skateboard-maintenance/",
    #     "https://blogbuz.co.uk/how-can-a-modern-power-station-transform-your-energy-efficiency/",
    #     "https://www.healthcarter.com/en-us/education/how-to-choose-the-best-portable-power-station-for-reliable-home-backup-power/",
    #     "https://londonincmagazine.ca/2025/05/01/solar-generators-for-homes/",
    #     "https://timeshealthmag.com/solar-generators-achieving-energy-independence-sustainably/",
    #     "https://durostech.com/how-to-choose-the-perfect-portable-power-station-for-your-needs/",
    #     "https://www.theglobeandmail.com/investing/markets/markets-news/GetNews/32575139/urtopia-champions-simplicity-with-its-elegant-city-e-bike-for-modern-commuters/",
    #     "https://www.thebikerguide.co.uk/motorcyclenews/read_207551/why-are-folding-electric-cycles-transforming-urban-commuting.html",
    #     "https://www.outdoorproject.com/users/discover-how-urban-ebikes-can-transform-your-daily-commute",
    #     "https://techbullion.com/discover-the-lightest-electric-bicycle-for-effortless-adventures/",
    #     "https://www.barchart.com/story/news/32560623/explore-premium-fat-tire-electric-bikes-for-high-performance-cycling",
    #     "https://www.therarewelshbit.com/5-ways-hotels-can-be-more-eco-friendly/",
    #     "https://celebstowiki.com/how-to-find-ipad-cases-supporting-creative-functionality/",
    #     "https://ultimatestatusbar.com/why-pick-a-detachable-keyboard-case-for-ipad/",
    #     "https://williamkamkwamba.com/set-up-microinverter-solar-kit/",
    #     "https://www.portotheme.com/how-to-integrate-ecoflow-delta-pro-ultra-with-rooftop-solar/",
    #     "https://houseofcoco.net/how-to-enhance-grid-tied-solar-with-battery-backup-solutions/",
    #     "https://www.aquionenergy.com/avoid-energy-waste-in-home-solar/",
    #     "https://techbullion.com/clou-ess-showed-up-at-re-boosting-industry-revenue-with-entire-lifecycle-service/",
    #     "https://www.uktech.news/other_news/clou-ess-makes-an-entrance-at-re-enhancing-sector-revenue-through-comprehensive-lifecycle-services",
    #     "https://techbar.org/the-essential-guide-to-electric-skateboard-maintenance/",
    #     "https://blogbuz.co.uk/how-can-a-modern-power-station-transform-your-energy-efficiency/",
    #     "https://www.healthcarter.com/en-us/education/how-to-choose-the-best-portable-power-station-for-reliable-home-backup-power/",
    #     "https://londonincmagazine.ca/2025/05/01/solar-generators-for-homes/",
    #     "https://timeshealthmag.com/solar-generators-achieving-energy-independence-sustainably/",
    #     "https://durostech.com/how-to-choose-the-perfect-portable-power-station-for-your-needs/",
    #     "https://www.theglobeandmail.com/investing/markets/markets-news/GetNews/32575139/urtopia-champions-simplicity-with-its-elegant-city-e-bike-for-modern-commuters/",
    #     "https://www.thebikerguide.co.uk/motorcyclenews/read_207551/why-are-folding-electric-cycles-transforming-urban-commuting.html",
    #     "https://www.outdoorproject.com/users/discover-how-urban-ebikes-can-transform-your-daily-commute",
    #     "https://techbullion.com/discover-the-lightest-electric-bicycle-for-effortless-adventures/",
    #     "https://www.barchart.com/story/news/32560623/explore-premium-fat-tire-electric-bikes-for-high-performance-cycling",
    #     "https://www.therarewelshbit.com/5-ways-hotels-can-be-more-eco-friendly/",
    #     "https://celebstowiki.com/how-to-find-ipad-cases-supporting-creative-functionality/",
    #     "https://ultimatestatusbar.com/why-pick-a-detachable-keyboard-case-for-ipad/",
    #     "https://williamkamkwamba.com/set-up-microinverter-solar-kit/",
    #     "https://www.thebikerguide.co.uk/motorcyclenews/read_207551/why-are-folding-electric-cycles-transforming-urban-commuting.html",
    #     "https://www.outdoorproject.com/users/discover-how-urban-ebikes-can-transform-your-daily-commute",
    #     "https://techbullion.com/discover-the-lightest-electric-bicycle-for-effortless-adventures/",
    #     "https://www.barchart.com/story/news/32560623/explore-premium-fat-tire-electric-bikes-for-high-performance-cycling",
    #     "https://www.therarewelshbit.com/5-ways-hotels-can-be-more-eco-friendly/",
    #     "https://celebstowiki.com/how-to-find-ipad-cases-supporting-creative-functionality/",
    #     "https://ultimatestatusbar.com/why-pick-a-detachable-keyboard-case-for-ipad/",
    #     "https://williamkamkwamba.com/set-up-microinverter-solar-kit/",
    #     "https://williamkamkwamba.com/set-up-microinverter-solar-kit/",
    #     "https://wunderbarkeit.de/leitfaden-zur-auswahl-der-perfekten-babytrage-fur-neugeborene/",
    #     "https://ludwigsburg-portal.de/milchproduktion-steigern-mit-freihaendigen-milchpumpen/",
    #     "https://www.thepinnaclelist.com/articles/tips-for-selecting-the-ideal-leather-recliner-for-comfort-and-support/",
    # ]
    
    target_urls = [
        "https://zh.wikipedia.org/wiki/%E5%A4%A7%E5%8B%B3%E4%BD%8D%E9%87%91%E5%B0%BA%E5%A4%A7%E7%B6%AC%E7%AB%A0",
        "https://zh.wikipedia.org/wiki/%E5%8A%A0%E5%8B%92%E6%AF%94%E6%B5%B7%E7%9B%972%EF%BC%9A%E8%81%9A%E9%AD%82%E6%A3%BA",
        "https://zh.wikipedia.org/wiki/%E9%81%A0%E7%A8%8B%E9%81%8E%E7%A8%8B%E8%AA%BF%E7%94%A8",
        "https://zh.wikipedia.org/wiki/%E6%80%A7%E8%A7%92%E8%89%B2%E6%89%AE%E6%BC%94",
        "https://zh.wikipedia.org/wiki/%E5%BE%AE%E6%9C%8D%E5%8B%99",
        "https://zh.wikipedia.org/wiki/Microsoft_Azure",
        "https://zh.wikipedia.org/wiki/Microsoft_Azure_%E5%84%B2%E5%AD%98%E9%AB%94",
        "https://zh.wikipedia.org/wiki/%E8%99%9B%E6%93%AC%E7%A7%81%E4%BA%BA%E7%B6%B2%E8%B7%AF"
    ]

    # 代理用户凭据池 - 从credentials文件中提取
    proxy_users = [
        {"username": "dp1_n6p5iypo", "password": "lIdIpNDSLKfWBaPp"},
        {"username": "dp1_j6xaudjt", "password": "MdmQRf7aHtvMZBsv"},
        {"username": "dp1_v9abt0zb", "password": "RDh0J8UMjA7ti1fu"},
        {"username": "dp1_v66t8aol", "password": "Z0EWTKPQqlxXQiHi"},
        {"username": "i8sdhd", "password": "bPU3dVjAOqL2"},
        {"username": "zesuwa", "password": "ZAEM66DzunVD"},
        {"username": "8a51ra", "password": "wJeaxnYW7MdQ"},
        {"username": "lu2kt2", "password": "CYlNTSKoUpW7"},
        {"username": "qfdsni", "password": "KTmNxoPWeUHF"},
        {"username": "ef2tqz", "password": "b4J4td38hknU"},
        {"username": "nr4ynw", "password": "lYbV7Y1Ee6UH"},
        {"username": "fgamz7", "password": "zKBRKcOKzbU0"},
        {"username": "woxb69", "password": "WiBOtwuTepC8"},
        {"username": "pmxa11", "password": "FaifJW8ozczA"},
        {"username": "n87v8u", "password": "ixnURsA8Q1Sc"},
        {"username": "ifhgc2", "password": "Hm7gSCCQRuKw"},
        {"username": "ate1zt", "password": "dsvglkL3iFv6"},
        {"username": "uueurg", "password": "94U5prYqVplE"},
        {"username": "ri3vjp", "password": "To8e8Vl7NVr2"},
        {"username": "ghdity", "password": "AwX3T9wnWIFQ"},
        {"username": "e1g1gy", "password": "YhQcg7FloURd"},
        {"username": "0w0hea", "password": "12CATdtOcvD4"},
        {"username": "xzc5px", "password": "aItnAMn0oono"},
        {"username": "vc9ryg", "password": "YyfTzKCfAnQQ"},
        {"username": "b9ur79", "password": "dhVYF4JSoy9W"},
        {"username": "4e4hsk", "password": "IyAMWboH1IYq"},
        {"username": "dhc011", "password": "F7vslrMvbvwm"},
        {"username": "4m9p3z", "password": "XEtS1rSWuo5m"},
        {"username": "t5lbk1", "password": "eRD8kRES38eh"},
        {"username": "zen4re", "password": "7dzVfeehqL5t"},
        {"username": "7w3o98", "password": "rp90XKtkukr4"},
        {"username": "v907wb", "password": "h3zEJ1RHnX37"},
        {"username": "fjm8ni", "password": "z5pZ8TbGzdmR"},
        {"username": "zecipi", "password": "8Cmof06fAeRz"},
        {"username": "vlfd6n", "password": "a39b1pf7FtgQ"},
        {"username": "ikexcy", "password": "K9FYNVtidFlO"},
        {"username": "uwhh6g", "password": "Is7B3Z6HDh92"},
        {"username": "0sl36r", "password": "RIqDRIZlrzQk"},
        {"username": "2jjdqv", "password": "9kGSTIDOYVER"},
        {"username": "wlwi9h", "password": "8hAUyQD8JYUS"},
        {"username": "38hn8k", "password": "SFQhafHavu1n"},
        {"username": "s06rj4", "password": "JzAQZO6M2RJp"},
        {"username": "68srkd", "password": "ClwNH6lv3jRk"},
        {"username": "kucp3u", "password": "tGbzpOeaYZKj"},
        {"username": "t7idk0", "password": "w0dIFNlXEyHN"},
        {"username": "097hj5", "password": "PlJ4dtH89qlw"},
        {"username": "rgtgfg", "password": "czTHZq4Ofpjm"},
        {"username": "dtiuvq", "password": "Kv1E6s8JiX7p"},
        {"username": "3iq6pn", "password": "IYVfnXCFIOTc"},
        {"username": "9g95l8", "password": "Ys8gGEqVBirt"},
        {"username": "ezkm4z", "password": "h5XWZ3x5rwbP"},
        {"username": "bhum2c", "password": "vSlMPQqK2XZE"},
        {"username": "m0qrrz", "password": "OLWSr8f6lCGM"},
        {"username": "oq3eke", "password": "wcUAvc9Vxr9A"},
        {"username": "bo1ym5", "password": "ZGCIbPyLGCJ1"},
        {"username": "f5ej3a", "password": "Ysa3yyDRPg3H"},
        {"username": "etgaoc", "password": "ELwTtBQwXaMH"},
        {"username": "c7ol0g", "password": "sZz9Yz5csPtX"},
        {"username": "u2lqnc", "password": "8TQLTgPDb0rO"},
        {"username": "xjffjh", "password": "WOUWfkLQaMUG"},
        {"username": "ospbry", "password": "mL81B5s9AWaA"},
        {"username": "x1xxxk", "password": "6PHEwmKk5xgh"},
        {"username": "m66bt9", "password": "ERRtmC7h9jXe"},
        {"username": "0o9r7f", "password": "5EPUbAg3tRML"},
        {"username": "ldsd4s", "password": "x1MTBIjwZqbk"},
        {"username": "7b1jyh", "password": "kabdJTwLgoym"},
        {"username": "ml46md", "password": "7ug3VnAKcAcO"},
        {"username": "u95te1", "password": "h0HCnJyRAMRX"},
        {"username": "6ggyy3", "password": "06h6IlhkSdaY"},
        {"username": "xfsqzm", "password": "C1CX0TEwgZJg"},
        {"username": "1algah", "password": "BpctQjllPl3K"},
        {"username": "1pyc4h", "password": "S2dqwpoc7H9F"},
        {"username": "tqs3gc", "password": "n3fFT4toTjPy"},
        {"username": "m1dcne", "password": "j11fq8UZywUO"},
        {"username": "t28yqd", "password": "6HKCYKu3AeoO"},
        {"username": "gb5irn", "password": "aeveb0VZ9cPz"},
        {"username": "qnalbi", "password": "70ynPW2AieQu"},
        {"username": "o76lop", "password": "5YOdZ952QfhK"},
        {"username": "52bv1j", "password": "RYzNV7gWtE1I"},
        {"username": "lbmc7c", "password": "zTLhKrrP2qo4"},
        {"username": "kmnou2", "password": "Brlxr78AiRPL"},
        {"username": "gstyti", "password": "G3ul4Nwz7oIZ"},
        {"username": "uuariz", "password": "aBjoLbD8eLt0"},
        {"username": "0a5usf", "password": "bOQQRcD0L0Ix"},
        {"username": "2urtzr", "password": "ZQh6pzrJqhrI"},
        {"username": "y33f9r", "password": "UXUwMzVft8FG"},
        {"username": "pjq6gx", "password": "7MUboSwmDTOK"},
        {"username": "ztdr15", "password": "9knZj8HY7Tdt"},
        {"username": "im7ctl", "password": "iMu3GUp5bl6R"},
        {"username": "5ocsdm", "password": "jG0WPqcMVfUw"},
        {"username": "ixqjir", "password": "Ptzfh5t1ycL2"},
        {"username": "t6gwen", "password": "MAz3J6wlbTWO"},
        {"username": "2s6wj9", "password": "0SkEsTegVV6t"},
        {"username": "6vjvbr", "password": "Wm38a6RhX2x6"},
        {"username": "3d83fa", "password": "KrolDKhuS88B"},
        {"username": "2p1muy", "password": "yk6mNb56JV7j"},
        {"username": "ao8dbh", "password": "DZ55dlB9Z7QM"},
        {"username": "2ysumc", "password": "oGgPuI14Sa3S"},
        {"username": "8ktq7w", "password": "Zfin9wj8Vtwc"},
        {"username": "rmwy1k", "password": "GtmVsy1WMSDc"},
        {"username": "p4k1dd", "password": "LObgTZ58sVDZ"},
        {"username": "wp4ah1", "password": "LboNQqIyesbn"},
        {"username": "tzh49c", "password": "smdnGN3iQjur"},
        {"username": "5q6wkf", "password": "qAQ6kO4dASMY"},
        {"username": "r3uhjt", "password": "gDAxsqNc1rvW"},
        {"username": "v7n515", "password": "5YpGd8nppJPQ"},
        {"username": "sowmlz", "password": "1KDZ3zk43OaQ"},
        {"username": "mxzr1a", "password": "bXqJNjdLqfYx"},
        {"username": "bme7vn", "password": "V2NU2XEMg2VJ"},
        {"username": "5faatm", "password": "vPieQL1SZeQH"},
        {"username": "44619b", "password": "a63DlieJ0PRr"},
        {"username": "r1b41v", "password": "6a61nm6WNR6o"},
        {"username": "nsfhtf", "password": "ojEd6US1mJXL"},
        {"username": "0k65yi", "password": "Ye6cuScAQxkl"},
        {"username": "yanswr", "password": "51f0Trym8Ue9"},
        {"username": "6qm1pd", "password": "eT9HykV46JFO"},
        {"username": "e89c7d", "password": "DsfTOvsUrtFs"},
        {"username": "lvdjk5", "password": "2DHBNTOgpsAH"},
        {"username": "w6zr2x", "password": "zU2ybEyfdO0H"},
        {"username": "holij1", "password": "78wuwqOUshbw"},
        {"username": "cwljrw", "password": "HidDDDcf0eR4"},
        {"username": "5auof3", "password": "MFB5b8jWZoli"},
        {"username": "0iy6ot", "password": "qZ73umSQNuOm"},
        {"username": "cw6af4", "password": "ZrT7hS8bptQX"},
        {"username": "3oquii", "password": "oX2NlKBpsaS5"},
        {"username": "r86hyn", "password": "BO1UZ8aL0P69"},
        {"username": "gpeyz4", "password": "jd2C1ldoahjX"},
        {"username": "q2992u", "password": "1PcOfG583Rhi"},
        {"username": "vpsn08", "password": "UjbXVS6OOlTf"},
        {"username": "wbunls", "password": "7j9SXYMHa2e7"},
        {"username": "k6mt3t", "password": "mixv7fPrA0F2"},
        {"username": "p9tw6k", "password": "NtTEHDS4bWdQ"},
        {"username": "0uon3a", "password": "lAjDMoLZ4TjS"},
        {"username": "lubsym", "password": "cF5X9xd5okGA"},
        {"username": "m0aajn", "password": "PRA2px72q8YQ"},
        {"username": "504khe", "password": "GGMjie8iWTBQ"},
        {"username": "mvf85h", "password": "l7FRXPJ8tUDW"},
        {"username": "p96qha", "password": "i3ReykTM7fwY"},
        {"username": "03qgwl", "password": "W2LXy5qERpwz"},
        {"username": "0o4bhj", "password": "P4Nn8sTPRvu7"},
        {"username": "j8j2u5", "password": "N8S9mZQMRpaV"},
        {"username": "84wdcz", "password": "mo7HSvwcqsoO"},
        {"username": "abp6hy", "password": "C4ghVCQRxepV"},
        {"username": "3htcuw", "password": "mLAiVTBT5a9w"},
        {"username": "s2mypp", "password": "FIXpfMp2yCIp"},
        {"username": "70w0o7", "password": "QNzTdoQT8WRE"},
        {"username": "eiviag", "password": "qGJMjhb9WQCe"},
        {"username": "tnm8vv", "password": "F52oU4xq6o0F"},
        {"username": "xa2kq9", "password": "jjhKOSbjTHh6"},
        {"username": "bsw94d", "password": "XbSbyw4hZ7Ra"},
        {"username": "jg7ttt", "password": "eJNEaV3NjTME"},
        {"username": "9m03k7", "password": "k0lRfab9BBsl"},
        {"username": "emkt1h", "password": "N7dNQl75JYuz"},
        {"username": "z1sz54", "password": "tKV8tjfhAba9"},
        {"username": "4yu31s", "password": "6yzEbRdJYZiX"},
        {"username": "05x7ij", "password": "1ubqL4f2Ccl6"},
        {"username": "y0mjii", "password": "IlY2Ers2DY1N"},
        {"username": "euqpw3", "password": "kKXvRc9THvbB"},
        {"username": "mbapba", "password": "KhkzHdXIBAbd"},
        {"username": "xqgvll", "password": "ZgutQTZTNMVC"},
        {"username": "rohznj", "password": "fdApfnmMpub5"},
        {"username": "tgw4hl", "password": "GRZtPXv90Xi4"},
        {"username": "n773tz", "password": "qMC3VCUhYPcq"},
        {"username": "iqjxk7", "password": "80WEn21byFa1"},
        {"username": "tqrluw", "password": "QBIbasK3wTHl"},
        {"username": "t9mtbm", "password": "b4xUTsH72IYG"},
        {"username": "11ljr6", "password": "USmGNID9lRuu"},
        {"username": "b30ipt", "password": "qlT7MpSUnxv1"},
        {"username": "s429kl", "password": "rJymQXqISvYN"},
        {"username": "1mf655", "password": "6HIrqQX44Yas"},
        {"username": "fx0lt9", "password": "2UpIpOj5VV0h"},
        {"username": "nlpuf7", "password": "lnPVM9REW9Po"},
        {"username": "2febzl", "password": "qgjACsbFEcAD"},
        {"username": "axqlyv", "password": "8Zq7468Krhmk"},
        {"username": "i9m8mh", "password": "oG983FCvJ7vU"},
        {"username": "rpi2cg", "password": "civ0TplM7h6W"},
        {"username": "h6xbce", "password": "l7XN95S8CMCr"},
        {"username": "7lhh9x", "password": "f1Nshpvlf7Nd"},
        {"username": "2xuwvg", "password": "1H7glsg9Z5sz"},
        {"username": "i48rpb", "password": "7DzcfflT2TDQ"}
        # 可以添加更多用户凭据
    ]
    
    wait_time = between(1, 3)  # 请求间隔1-3秒
    
    def on_start(self):
        """初始化用户会话"""
        # 随机选择一个代理用户
        self.proxy_user = random.choice(self.proxy_users)
        
        # 配置代理设置
        self.proxy_host = "192.168.132.58"  # 根据实际情况修改
        self.proxy_port = "7891"
        
        # 设置代理
        self.client.proxies = {
            'http': f'http://{self.proxy_user["username"]}:{self.proxy_user["password"]}@{self.proxy_host}:{self.proxy_port}',
            'https': f'http://{self.proxy_user["username"]}:{self.proxy_user["password"]}@{self.proxy_host}:{self.proxy_port}'
        }
        
        # 设置超时
        self.client.timeout = 30
        
        print(f"用户 {self.proxy_user['username']} 开始测试")
    
    @task(1)
    def test_simple_get(self):
        """简单GET请求测试 - 权重1"""
        url = random.choice(self.target_urls)
        
        try:
            with self.client.get(
                url, 
                catch_response=True,
                name="simple_get"
            ) as response:
                if response.status_code == 200:
                    response.success()
                else:
                    response.failure(f"状态码: {response.status_code}")
        except Exception as e:
            print(f"请求失败: {e}")
    

    


class SystemMonitor:
    """系统资源监控器"""
    
    def __init__(self):
        self.monitoring = False
        self.stats = []
        self.monitor_thread = None
    
    def start_monitoring(self):
        """开始监控"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        print("系统监控已启动")
    
    def stop_monitoring(self):
        """停止监控"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        print("系统监控已停止")
    
    def _monitor_loop(self):
        """监控循环"""
        while self.monitoring:
            try:
                # 获取系统资源使用情况
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                # 尝试获取clash-meta进程信息
                clash_process = None
                for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
                    if 'mihomo' in proc.info['name'].lower() or 'clash' in proc.info['name'].lower():
                        clash_process = proc.info
                        break
                
                stat = {
                    'timestamp': datetime.now().isoformat(),
                    'system_cpu': cpu_percent,
                    'system_memory_percent': memory.percent,
                    'system_memory_used_mb': memory.used / 1024 / 1024,
                    'clash_process': clash_process
                }
                
                self.stats.append(stat)
                
            except Exception as e:
                print(f"监控错误: {e}")
            
            time.sleep(5)  # 每5秒采集一次
    
    def save_stats(self, filename="system_stats.json"):
        """保存监控数据"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2, ensure_ascii=False)
        print(f"监控数据已保存到 {filename}")


# 全局监控器实例
monitor = SystemMonitor()


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """测试开始时的回调"""
    print("=== Clash-Meta 压力测试开始 ===")
    print(f"目标代理: 192.168.132.58:7891")
    print(f"测试用户数: {len(ProxyUser.proxy_users)}")
    print(f"目标URL数: {len(ProxyUser.target_urls)}")
    monitor.start_monitoring()


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """测试结束时的回调"""
    print("=== Clash-Meta 压力测试结束 ===")
    monitor.stop_monitoring()
    
    # 保存监控数据
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    monitor.save_stats(f"clash_meta_stats_{timestamp}.json")
    
    # 打印测试总结
    stats = environment.stats
    print(f"\n=== 测试总结 ===")
    print(f"总请求数: {stats.total.num_requests}")
    print(f"失败请求数: {stats.total.num_failures}")
    print(f"平均响应时间: {stats.total.avg_response_time:.2f}ms")
    print(f"最大响应时间: {stats.total.max_response_time}ms")
    print(f"RPS: {stats.total.current_rps:.2f}")


if __name__ == "__main__":
    print("请使用 locust 命令运行此脚本:")
    print("locust -f locustfile.py --host=http://localhost")
    print("或者使用 Web UI: locust -f locustfile.py --host=http://localhost --web-host=0.0.0.0")