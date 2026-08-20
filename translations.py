# -*- coding: utf-8 -*-
"""Centralized translation dictionary for the whole app (AR default / FR)."""

TR = {
    "app_name": {"ar": "المخيم الصيفي", "fr": "Camp d'Été"},
    "lang_toggle": {"ar": "Français", "fr": "العربية"},

    # Auth
    "login": {"ar": "تسجيل الدخول", "fr": "Connexion"},
    "logout": {"ar": "تسجيل الخروج", "fr": "Déconnexion"},
    "username": {"ar": "اسم المستخدم", "fr": "Nom d'utilisateur"},
    "password": {"ar": "كلمة المرور", "fr": "Mot de passe"},
    "login_btn": {"ar": "دخول", "fr": "Se connecter"},
    "login_error": {"ar": "اسم المستخدم أو كلمة المرور غير صحيحة", "fr": "Identifiant ou mot de passe incorrect"},
    "welcome_admin": {"ar": "مرحباً بك في لوحة تحكم المخيم الصيفي", "fr": "Bienvenue dans le tableau de bord du camp"},

    # Nav - Admin
    "nav_dashboard": {"ar": "لوحة التحكم", "fr": "Tableau de bord"},
    "nav_participants": {"ar": "المشاركون", "fr": "Participants"},
    "nav_rooms": {"ar": "الغرف", "fr": "Chambres"},
    "nav_attendance": {"ar": "الحضور", "fr": "Présence"},
    "nav_payments": {"ar": "الاشتراكات", "fr": "Cotisations"},
    "nav_transport": {"ar": "النقل", "fr": "Transport"},
    "nav_announcements": {"ar": "الإعلانات", "fr": "Annonces"},
    "nav_camp_info": {"ar": "معلومات المخيم", "fr": "Infos du camp"},
    "nav_admins": {"ar": "المسؤولون", "fr": "Administrateurs"},
    "nav_settings": {"ar": "الإعدادات", "fr": "Paramètres"},
    "nav_logs": {"ar": "سجل النشاط", "fr": "Journal d'activité"},

    # Nav - Participant
    "nav_home": {"ar": "الرئيسية", "fr": "Accueil"},
    "nav_my_info": {"ar": "معلوماتي", "fr": "Mes informations"},
    "nav_my_room": {"ar": "غرفتي", "fr": "Ma chambre"},
    "nav_my_qr": {"ar": "QR الخاص بي", "fr": "Mon QR"},

    # Stats
    "stats": {"ar": "الإحصائيات", "fr": "Statistiques"},
    "total_participants": {"ar": "إجمالي المشاركين", "fr": "Total participants"},
    "present_count": {"ar": "عدد الحاضرين", "fr": "Présents"},
    "absent_count": {"ar": "عدد الغائبين", "fr": "Absents"},
    "paid_count": {"ar": "دفعوا الاشتراك", "fr": "Ont payé"},
    "unpaid_count": {"ar": "لم يدفعوا", "fr": "Non payé"},
    "total_subs": {"ar": "مجموع الاشتراكات", "fr": "Total cotisations"},
    "total_paid": {"ar": "المبلغ المدفوع", "fr": "Montant payé"},
    "total_remaining": {"ar": "المبلغ المتبقي", "fr": "Montant restant"},
    "rooms_count": {"ar": "عدد الغرف", "fr": "Nombre de chambres"},
    "places_remaining": {"ar": "الأماكن المتبقية", "fr": "Places restantes"},

    # Participant fields
    "first_name": {"ar": "الاسم", "fr": "Prénom"},
    "last_name": {"ar": "اللقب", "fr": "Nom"},
    "wilaya": {"ar": "الولاية", "fr": "Wilaya"},
    "phone": {"ar": "رقم الهاتف", "fr": "Téléphone"},
    "transport": {"ar": "وسيلة النقل", "fr": "Moyen de transport"},
    "entry_date": {"ar": "تاريخ الدخول", "fr": "Date d'entrée"},
    "reg_id": {"ar": "رقم التسجيل", "fr": "N° d'inscription"},
    "room": {"ar": "الغرفة", "fr": "Chambre"},
    "place": {"ar": "المكان", "fr": "Place"},
    "sub_amount": {"ar": "الاشتراك", "fr": "Cotisation"},
    "payment_status": {"ar": "حالة الدفع", "fr": "Statut de paiement"},
    "attendance_status": {"ar": "حالة الحضور", "fr": "Statut de présence"},
    "notes": {"ar": "ملاحظات", "fr": "Remarques"},
    "amount_required": {"ar": "المبلغ المطلوب", "fr": "Montant requis"},
    "amount_paid": {"ar": "المبلغ المدفوع", "fr": "Montant payé"},
    "amount_remaining": {"ar": "المبلغ المتبقي", "fr": "Montant restant"},

    # Payment statuses
    "paid": {"ar": "مدفوع", "fr": "Payé"},
    "unpaid": {"ar": "غير مدفوع", "fr": "Non payé"},
    "partial": {"ar": "دفع جزئي", "fr": "Paiement partiel"},

    # Attendance statuses
    "present": {"ar": "حاضر", "fr": "Présent"},
    "not_recorded": {"ar": "لم يتم تسجيل الحضور", "fr": "Présence non enregistrée"},
    "mark_attendance": {"ar": "تسجيل الحضور", "fr": "Enregistrer la présence"},
    "attendance_recorded": {"ar": "تم تسجيل الحضور بنجاح", "fr": "Présence enregistrée avec succès"},

    # Transport options
    "bus": {"ar": "حافلة", "fr": "Bus"},
    "private_car": {"ar": "سيارة شخصية", "fr": "Voiture personnelle"},
    "private_transport": {"ar": "نقل خاص", "fr": "Transport privé"},
    "no_transport": {"ar": "بدون نقل", "fr": "Sans transport"},
    "other": {"ar": "أخرى", "fr": "Autre"},

    # Rooms
    "room_number": {"ar": "رقم الغرفة", "fr": "N° de chambre"},
    "room_name": {"ar": "اسم الغرفة", "fr": "Nom de la chambre"},
    "capacity": {"ar": "السعة", "fr": "Capacité"},
    "current_participants": {"ar": "عدد المشاركين في الغرفة", "fr": "Participants dans la chambre"},
    "remaining_places": {"ar": "الأماكن المتبقية", "fr": "Places restantes"},
    "room_total_subs": {"ar": "مجموع اشتراكات الغرفة", "fr": "Total cotisations de la chambre"},
    "your_place": {"ar": "مكانك", "fr": "Votre place"},
    "of": {"ar": "من", "fr": "sur"},
    "roommates": {"ar": "المشاركون معك في الغرفة", "fr": "Vos colocataires"},

    # Actions
    "add": {"ar": "إضافة", "fr": "Ajouter"},
    "edit": {"ar": "تعديل", "fr": "Modifier"},
    "delete": {"ar": "حذف", "fr": "Supprimer"},
    "save": {"ar": "حفظ", "fr": "Enregistrer"},
    "cancel": {"ar": "إلغاء", "fr": "Annuler"},
    "search": {"ar": "بحث", "fr": "Rechercher"},
    "filter": {"ar": "تصفية", "fr": "Filtrer"},
    "export": {"ar": "تصدير", "fr": "Exporter"},
    "print_card": {"ar": "طباعة البطاقة", "fr": "Imprimer la carte"},
    "confirm_delete": {"ar": "هل أنت متأكد من الحذف؟", "fr": "Confirmer la suppression ?"},
    "yes": {"ar": "نعم", "fr": "Oui"},
    "no": {"ar": "لا", "fr": "Non"},
    "success_add": {"ar": "تمت الإضافة بنجاح", "fr": "Ajouté avec succès"},
    "success_update": {"ar": "تم التعديل بنجاح", "fr": "Modifié avec succès"},
    "success_delete": {"ar": "تم الحذف بنجاح", "fr": "Supprimé avec succès"},
    "all": {"ar": "الكل", "fr": "Tous"},

    # Participant list
    "participant_list": {"ar": "لائحة المشاركين", "fr": "Liste des participants"},
    "add_participant": {"ar": "إضافة مشارك", "fr": "Ajouter un participant"},
    "edit_participant": {"ar": "تعديل مشارك", "fr": "Modifier un participant"},
    "no_results": {"ar": "لا توجد نتائج", "fr": "Aucun résultat"},
    "duplicate_warning": {"ar": "تحذير: رقم الهاتف مسجل مسبقاً لمشارك آخر", "fr": "Attention : ce numéro de téléphone existe déjà"},

    # QR / Card
    "participant_card": {"ar": "بطاقة المشارك", "fr": "Carte du participant"},
    "my_qr": {"ar": "QR الخاص بي", "fr": "Mon code QR"},
    "scan_qr": {"ar": "مسح رمز QR", "fr": "Scanner le QR"},
    "enter_token": {"ar": "أدخل الرمز السري", "fr": "Entrez le code secret"},

    # Camp info
    "camp_program": {"ar": "برنامج المخيم", "fr": "Programme du camp"},
    "start_date": {"ar": "تاريخ البداية", "fr": "Date de début"},
    "end_date": {"ar": "تاريخ النهاية", "fr": "Date de fin"},
    "camp_location": {"ar": "مكان المخيم", "fr": "Lieu du camp"},
    "gather_time": {"ar": "وقت التجمع", "fr": "Heure de rassemblement"},
    "gather_place": {"ar": "مكان التجمع", "fr": "Lieu de rassemblement"},
    "access_instructions": {"ar": "تعليمات الوصول", "fr": "Instructions d'accès"},
    "required_items": {"ar": "الأشياء المطلوبة", "fr": "Objets requis"},
    "rules": {"ar": "القوانين", "fr": "Règlement"},
    "important_info": {"ar": "معلومات مهمة", "fr": "Informations importantes"},
    "contact_numbers": {"ar": "أرقام التواصل الرسمية", "fr": "Numéros de contact officiels"},

    # Announcements
    "announcements": {"ar": "الإعلانات", "fr": "Annonces"},
    "title": {"ar": "العنوان", "fr": "Titre"},
    "content": {"ar": "المحتوى", "fr": "Contenu"},
    "priority": {"ar": "الأولوية", "fr": "Priorité"},
    "normal": {"ar": "عادي", "fr": "Normal"},
    "important": {"ar": "مهم", "fr": "Important"},
    "urgent": {"ar": "عاجل", "fr": "Urgent"},

    # Admins
    "add_admin": {"ar": "إضافة مسؤول", "fr": "Ajouter un administrateur"},
    "role": {"ar": "الصلاحية", "fr": "Rôle"},
    "super_admin": {"ar": "المدير الرئيسي", "fr": "Administrateur principal"},
    "admin": {"ar": "مدير", "fr": "Administrateur"},
    "full_name": {"ar": "الاسم الكامل", "fr": "Nom complet"},

    # Misc
    "settings": {"ar": "الإعدادات", "fr": "Paramètres"},
    "back": {"ar": "رجوع", "fr": "Retour"},
    "date": {"ar": "التاريخ", "fr": "Date"},
    "time": {"ar": "الوقت", "fr": "Heure"},
    "action": {"ar": "الإجراء", "fr": "Action"},
    "by": {"ar": "بواسطة", "fr": "Par"},
    "currency": {"ar": "دج", "fr": "DA"},
    "attendance_day": {"ar": "يوم الحضور", "fr": "Jour de présence"},
    "add_day": {"ar": "إضافة يوم", "fr": "Ajouter un jour"},
    "app_url": {"ar": "رابط التطبيق (لِرمز QR)", "fr": "URL de l'application (pour le QR)"},
    "bed_label": {"ar": "تسمية المكان", "fr": "Nom du champ place"},
    "show_roommates": {"ar": "إظهار أسماء زملاء الغرفة للمشاركين", "fr": "Afficher les noms des colocataires"},
    "invalid_token": {"ar": "الرمز غير صالح، تحقق من الرابط", "fr": "Code invalide, vérifiez le lien"},
    "not_assigned": {"ar": "غير محدد", "fr": "Non défini"},
    "backup": {"ar": "نسخة احتياطية", "fr": "Sauvegarde"},
    "download_backup": {"ar": "تحميل نسخة احتياطية من القاعدة", "fr": "Télécharger une sauvegarde de la base"},
    "activity_log": {"ar": "سجل النشاط", "fr": "Journal d'activité"},
    "global_search": {"ar": "بحث شامل", "fr": "Recherche globale"},
    "occupancy": {"ar": "نسبة الإشغال", "fr": "Taux d'occupation"},
    "assign_room": {"ar": "تعيين الغرفة", "fr": "Assigner la chambre"},
    "no_room": {"ar": "بدون غرفة", "fr": "Sans chambre"},
    "portal_intro": {"ar": "أدخل رابطك الشخصي أو امسح رمز QR الخاص بك للوصول إلى بوابتك", "fr": "Entrez votre lien personnel ou scannez votre QR pour accéder à votre portail"},
    "go": {"ar": "دخول", "fr": "Accéder"},
}


def t(key: str, lang: str) -> str:
    entry = TR.get(key)
    if not entry:
        return key
    return entry.get(lang, entry.get("ar", key))
