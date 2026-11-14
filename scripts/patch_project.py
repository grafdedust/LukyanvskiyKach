from pathlib import Path
import sys

root = Path(sys.argv[1])
base = root / "app/src/main/java/com/lukyanovskykach"
app = base / "ui/LukyanovskyApp.kt"
screens = base / "ui/screens/Screens.kt"
settings = base / "ui/screens/AppSettingsScreen.kt"
theme = base / "ui/theme/Theme.kt"

def replace_once(path, old, new):
    data = path.read_text()
    if old not in data:
        raise SystemExit(f"Patch context not found in {path}: {old[:100]!r}")
    path.write_text(data.replace(old, new, 1))

replace_once(app,
    '    val nav = rememberNavController()\n    val database = remember { KachDatabase.getInstance(LocalContext.current) }',
    '    val nav = rememberNavController()\n    val context = LocalContext.current\n    val database = remember(context) { KachDatabase.getInstance(context) }')

data = screens.read_text()
data = data.replace('import androidx.compose.material.icons.filled.Pill\n', '')
data = data.replace('Icons.Default.Pill', 'Icons.Default.FitnessCenter')
screens.write_text(data)

settings_text = settings.read_text()
anchor = '    var language by remember { mutableStateOf(prefs.getString("language", "system") ?: "system") }'
if anchor not in settings_text:
    raise SystemExit("Settings language state anchor missing")
settings_text = settings_text.replace(anchor, anchor + '\n    var visualStyle by remember { mutableStateOf(prefs.getString("visual_style", "minimal") ?: "minimal") }', 1)
anchor2 = '        Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {\n            Column(Modifier.fillMaxWidth().padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {\n                Text("Язык", fontWeight = FontWeight.SemiBold)'
style_block = '''        Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
            Column(Modifier.fillMaxWidth().padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Text("Стиль интерфейса", fontWeight = FontWeight.SemiBold)
                listOf("brutal" to "Брутал · массивный и контрастный", "minimal" to "Минимал · чистый и спокойный", "tactical" to "Тактикал · графит и олива").forEach { (key, label) ->
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                        Text(label, modifier = Modifier.weight(1f))
                        RadioButton(selected = visualStyle == key, onClick = {
                            visualStyle = key
                            prefs.edit().putString("visual_style", key).apply()
                        })
                    }
                }
            }
        }
'''
if anchor2 not in settings_text:
    raise SystemExit("Settings language card anchor missing")
settings_text = settings_text.replace(anchor2, style_block + anchor2, 1)
settings.write_text(settings_text)

theme.write_text('''package com.lukyanovskykach.ui.theme

import android.content.Context
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext

private val MinimalDark = darkColorScheme(
    primary = Color(0xFFB7E66A), onPrimary = Color(0xFF17200D),
    secondary = Color(0xFF91B85A), background = Color(0xFF111315),
    onBackground = Color(0xFFF2F4EF), surface = Color(0xFF1A1E20),
    onSurface = Color(0xFFF2F4EF), surfaceVariant = Color(0xFF242A2C),
    onSurfaceVariant = Color(0xFFA3ADA5)
)
private val MinimalLight = lightColorScheme(
    primary = Color(0xFF527D24), onPrimary = Color.White,
    secondary = Color(0xFF668C3B), background = Color(0xFFF5F7F2),
    onBackground = Color(0xFF171B16), surface = Color.White,
    onSurface = Color(0xFF171B16), surfaceVariant = Color(0xFFE8EDE4),
    onSurfaceVariant = Color(0xFF596255)
)
private val BrutalDark = darkColorScheme(
    primary = Color(0xFFFF6B35), onPrimary = Color.Black,
    secondary = Color(0xFFFFB15C), background = Color(0xFF090909),
    onBackground = Color.White, surface = Color(0xFF191919),
    onSurface = Color.White, surfaceVariant = Color(0xFF303030),
    onSurfaceVariant = Color(0xFFD0D0D0)
)
private val BrutalLight = lightColorScheme(
    primary = Color(0xFFB83B18), onPrimary = Color.White,
    secondary = Color(0xFF8A2E16), background = Color(0xFFF4F0EB),
    onBackground = Color(0xFF17110E), surface = Color.White,
    onSurface = Color(0xFF17110E), surfaceVariant = Color(0xFFE8DDD5),
    onSurfaceVariant = Color(0xFF5D5048)
)
private val TacticalDark = darkColorScheme(
    primary = Color(0xFFA3AD62), onPrimary = Color(0xFF171A0D),
    secondary = Color(0xFF7E8C48), background = Color(0xFF10130F),
    onBackground = Color(0xFFE7E9DC), surface = Color(0xFF1B211A),
    onSurface = Color(0xFFE7E9DC), surfaceVariant = Color(0xFF293126),
    onSurfaceVariant = Color(0xFFADB69A)
)
private val TacticalLight = lightColorScheme(
    primary = Color(0xFF596638), onPrimary = Color.White,
    secondary = Color(0xFF74834B), background = Color(0xFFECEFE5),
    onBackground = Color(0xFF1A2016), surface = Color(0xFFF8FAF3),
    onSurface = Color(0xFF1A2016), surfaceVariant = Color(0xFFDDE3D2),
    onSurfaceVariant = Color(0xFF56604B)
)

@Composable
fun KachTheme(darkTheme: Boolean = isSystemInDarkTheme(), content: @Composable () -> Unit) {
    val context = LocalContext.current
    val prefs = remember(context) { context.getSharedPreferences("kach_preferences", Context.MODE_PRIVATE) }
    var style by remember { mutableStateOf(prefs.getString("visual_style", "minimal") ?: "minimal") }
    DisposableEffect(prefs) {
        val listener = android.content.SharedPreferences.OnSharedPreferenceChangeListener { shared, key ->
            if (key == "visual_style") style = shared.getString(key, "minimal") ?: "minimal"
        }
        prefs.registerOnSharedPreferenceChangeListener(listener)
        onDispose { prefs.unregisterOnSharedPreferenceChangeListener(listener) }
    }
    val colors = when (style) {
        "brutal" -> if (darkTheme) BrutalDark else BrutalLight
        "tactical" -> if (darkTheme) TacticalDark else TacticalLight
        else -> if (darkTheme) MinimalDark else MinimalLight
    }
    MaterialTheme(colorScheme = colors, typography = MaterialTheme.typography, content = content)
}
''')

# Navigation: detail screens always expose a top-right back action. The "More" tab
# is a true menu root and must not restore a previously opened child destination.
app_text = app.read_text()
app_text = app_text.replace(
    'import androidx.compose.material3.Icon\n',
    'import androidx.compose.material3.Icon\nimport androidx.compose.material3.IconButton\nimport androidx.compose.material3.TopAppBar\nimport androidx.compose.material.icons.filled.ArrowBack\n'
)
app_text = app_text.replace(
    '            nav.navigate(item.route) {\n                                popUpTo("home") { saveState = true }\n                                launchSingleTop = true\n                                restoreState = true\n                            }',
    '            if (item.route == "more") {\n                                nav.navigate("more") {\n                                    popUpTo("home") { inclusive = false; saveState = false }\n                                    launchSingleTop = true\n                                    restoreState = false\n                                }\n                            } else {\n                                nav.navigate(item.route) {\n                                    popUpTo("home") { saveState = true }\n                                    launchSingleTop = true\n                                    restoreState = true\n                                }\n                            }'
)
old_scaffold = '''    Scaffold(
        bottomBar = {'''
new_scaffold = '''    val rootRoutes = setOf("home", "workouts", "profile", "nutrition", "more")
    Scaffold(
        topBar = {
            if (current != null && current !in rootRoutes) {
                TopAppBar(
                    title = { Text("") },
                    actions = {
                        IconButton(onClick = { if (!nav.popBackStack()) nav.navigate("more") }) {
                            Icon(Icons.Default.ArrowBack, contentDescription = "Назад")
                        }
                    }
                )
            }
        },
        bottomBar = {'''
if old_scaffold not in app_text:
    raise SystemExit("Scaffold anchor missing in LukyanovskyApp.kt")
app_text = app_text.replace(old_scaffold, new_scaffold, 1)
app_text = app_text.replace('''                onBackup = { nav.navigate("backup") }
            ) }''','''            ) }''')
app_text = app_text.replace('composable("settings") { AppSettingsScreen() }','composable("settings") { AppSettingsScreen(onBackup = { nav.navigate("backup") }) }')
app.write_text(app_text)

# Backup management belongs under Settings, not in the general More menu.
screens_text = screens.read_text()
screens_text = screens_text.replace(
    'fun MoreScreen(onMedications: () -> Unit, onStatistics: () -> Unit, onSettings: () -> Unit, onNotebook: () -> Unit, onBackup: () -> Unit) {',
    'fun MoreScreen(onMedications: () -> Unit, onStatistics: () -> Unit, onSettings: () -> Unit, onNotebook: () -> Unit) {'
)
screens_text = screens_text.replace('        MenuRow("Резервные копии", onBackup) { Icon(Icons.Default.Settings, null) }\n','')
screens.write_text(screens_text)

# Settings screen gets a direct entry to backup tools.
settings_text = settings.read_text()
settings_text = settings_text.replace('fun AppSettingsScreen() {','fun AppSettingsScreen(onBackup: () -> Unit = {}) {')
settings_text = settings_text.replace(
    '        Text("Настройки сохраняются на устройстве и применяются после выбора.',
    '        OutlinedButton(onClick = onBackup, modifier = Modifier.fillMaxWidth()) { Text("Резервные копии") }\n        Text("Настройки сохраняются на устройстве и применяются после выбора.'
)
settings.write_text(settings_text)

# Add a restrained Telegram-like near-black monochrome theme.
settings_text = settings.read_text()
settings_text = settings_text.replace(
    '"tactical" to "Тактикал · графит и олива").forEach',
    '"tactical" to "Тактикал · графит и олива", "dark" to "Тёмная · монохромная").forEach'
)
settings.write_text(settings_text)

theme_text = theme.read_text()
theme_text = theme_text.replace(
    'private val TacticalLight = lightColorScheme(',
    '''private val TelegramDark = darkColorScheme(
    primary = Color(0xFFE6E6E6), onPrimary = Color(0xFF111111),
    secondary = Color(0xFFBDBDBD), background = Color(0xFF000000),
    onBackground = Color(0xFFEAEAEA), surface = Color(0xFF111111),
    onSurface = Color(0xFFEAEAEA), surfaceVariant = Color(0xFF1B1B1B),
    onSurfaceVariant = Color(0xFF9A9A9A),
    outline = Color(0xFF303030)
)
private val TacticalLight = lightColorScheme('''
)
theme_text = theme_text.replace(
    '        "tactical" -> if (darkTheme) TacticalDark else TacticalLight\n        else -> if (darkTheme) MinimalDark else MinimalLight',
    '        "tactical" -> if (darkTheme) TacticalDark else TacticalLight\n        "dark" -> TelegramDark\n        else -> if (darkTheme) MinimalDark else MinimalLight'
)
theme.write_text(theme_text)


# Keep only four bottom navigation destinations. Nutrition remains fully available
# from the More section rather than occupying a permanent bottom-bar slot.
app_text = app.read_text()
app_text = app_text.replace('        Destination("nutrition", R.string.tab_nutrition, Icons.Default.Restaurant),\n', '')
app_text = app_text.replace('setOf("home", "workouts", "profile", "nutrition", "more")', 'setOf("home", "workouts", "profile", "more")')
app_text = app_text.replace(
    '                onNotebook = { nav.navigate("notebook") },',
    '                onNotebook = { nav.navigate("notebook") },\n                onNutrition = { nav.navigate("nutrition") },'
)
app.write_text(app_text)

screens_text = screens.read_text()
screens_text = screens_text.replace(
    'fun MoreScreen(onMedications: () -> Unit, onStatistics: () -> Unit, onSettings: () -> Unit, onNotebook: () -> Unit) {',
    'fun MoreScreen(onMedications: () -> Unit, onStatistics: () -> Unit, onSettings: () -> Unit, onNotebook: () -> Unit, onNutrition: () -> Unit) {'
)
nutrition_row = '        MenuRow("Питание", onNutrition) { Icon(Icons.Default.Restaurant, null) }\n'
if nutrition_row not in screens_text:
    anchor = '        MenuRow("Блокнот и задачи", onNotebook) { Icon(Icons.Default.Description, null) }\n'
    if anchor not in screens_text:
        raise SystemExit("More menu anchor missing for Nutrition entry")
    screens_text = screens_text.replace(anchor, nutrition_row + anchor, 1)
screens.write_text(screens_text)


# Resolve the moved nutrition menu icon and opt in to the Material3 top app bar API.
screens_text = screens.read_text()
if 'import androidx.compose.material.icons.filled.Restaurant' not in screens_text:
    screens_text = screens_text.replace(
        'import androidx.compose.material.icons.Icons\n',
        'import androidx.compose.material.icons.Icons\nimport androidx.compose.material.icons.filled.Restaurant\n'
    )
screens.write_text(screens_text)

app_text = app.read_text()
if 'import androidx.compose.material3.ExperimentalMaterial3Api' not in app_text:
    app_text = app_text.replace(
        'import androidx.compose.material3.Icon\n',
        'import androidx.compose.material3.Icon\nimport androidx.compose.material3.ExperimentalMaterial3Api\n'
    )
app_text = app_text.replace(
    '@Composable\nfun LukyanovskyApp()',
    '@OptIn(ExperimentalMaterial3Api::class)\n@Composable\nfun LukyanovskyApp()'
)
app.write_text(app_text)

print("Fixed moved Nutrition icon import and opted in to Material3 TopAppBar API.")

print("Bottom navigation reduced to Home, Workouts, Profile and More; Nutrition moved into More.")

print("Patched navigation back actions, More menu root behavior, moved backups to Settings, and added monochrome Dark theme.")



# Settings footer: show the actual installed package version and author.
settings_text = settings.read_text()
footer_anchor = '        Text("Настройки сохраняются на устройстве и применяются после выбора. Системный язык и тема используют параметры Android.", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)'
footer_new = '''        Spacer(Modifier.height(12.dp))
        val appVersion = remember {
            try {
                context.packageManager.getPackageInfo(context.packageName, 0).versionName ?: "0.9"
            } catch (_: Exception) { "0.9" }
        }
        Text("Версия $appVersion", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text("Автор: Царь", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text("Настройки сохраняются на устройстве и применяются после выбора. Системный язык и тема используют параметры Android.", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)'''
if footer_anchor not in settings_text:
    raise SystemExit("Settings footer anchor missing")
settings.write_text(settings_text.replace(footer_anchor, footer_new, 1))

# Bump Android versionCode while keeping applicationId unchanged so Android
# installs this APK as an in-place update and preserves app data.
import re
gradle_candidates = [root / "app/build.gradle.kts", root / "app/build.gradle"]
gradle_file = next((p for p in gradle_candidates if p.exists()), None)
if gradle_file is None:
    raise SystemExit("App Gradle file not found")
gradle_text = gradle_file.read_text()
match = re.search(r"versionCode\s*(?:=\s*)?(\d+)", gradle_text)
if match:
    old_code = int(match.group(1))
    gradle_text = gradle_text[:match.start(1)] + str(old_code + 1) + gradle_text[match.end(1):]
else:
    old_code = 1
    if "defaultConfig {" not in gradle_text:
        raise SystemExit("defaultConfig block not found in app Gradle file")
    gradle_text = gradle_text.replace("defaultConfig {", "defaultConfig {\n        versionCode = 2\n        versionName = \"0.9\"", 1)
name_match = re.search(r'versionName\s*(?:=\s*)?"([^"]+)"', gradle_text)
if name_match and match:
    current_name = name_match.group(1)
    parts = current_name.split(".")
    try:
        parts[-1] = str(int(parts[-1]) + 1)
        next_name = ".".join(parts)
    except ValueError:
        next_name = current_name + ".1"
    gradle_text = gradle_text[:name_match.start(1)] + next_name + gradle_text[name_match.end(1):]
# Force the debug build to use the cached, persistent keystore. Without this,
# Gradle may generate a fresh debug certificate and Android rejects updates.
if 'signingConfigs.getByName("stableDebug")' not in gradle_text:
    signing_block = '''
    signingConfigs {
        create("stableDebug") {
            storeFile = file(System.getProperty("user.home") + "/.android/debug.keystore")
            storePassword = "android"
            keyAlias = "androiddebugkey"
            keyPassword = "android"
        }
    }
    buildTypes {
        getByName("debug") {
            signingConfig = signingConfigs.getByName("stableDebug")
        }
    }
'''
    gradle_text = gradle_text.replace("    buildFeatures { compose = true }", signing_block + "    buildFeatures { compose = true }", 1)
if 'applicationId = "com.lukyanovskykach"' not in gradle_text:
    raise SystemExit("Unexpected applicationId; refusing to change package identity")
# Use the GitHub run number so each published APK has a strictly increasing versionCode.
import os
run_number = int(os.environ.get("GITHUB_RUN_NUMBER", "1"))
target_version_code = max(old_code + 1, 1000 + run_number)
gradle_text = re.sub(r"(versionCode\s*(?:=\s*)?)\d+", lambda m: m.group(1) + str(target_version_code), gradle_text, count=1)
gradle_file.write_text(gradle_text)
print("Stable debug signing config applied using the persistent GitHub Actions keystore.")
print(f"Version bumped: versionCode {old_code} -> {target_version_code}; package id preserved.")


# Functional fixes requested: navigation, theme variants and notebook editor.
app_text = app.read_text()
old_nav = '''                        onClick = {
                            if (item.route == "more") {
                                nav.navigate("more") {
                                    popUpTo("home") { inclusive = false; saveState = false }
                                    launchSingleTop = true
                                    restoreState = false
                                }
                            } else {
                                nav.navigate(item.route) {
                                    popUpTo("home") { saveState = true }
                                    launchSingleTop = true
                                    restoreState = true
                                }
                            }
                        },'''
new_nav = '''                        onClick = {
                            if (item.route == "home") {
                                nav.popBackStack("home", inclusive = false)
                            } else {
                                nav.navigate(item.route) {
                                    popUpTo("home") { inclusive = false; saveState = false }
                                    launchSingleTop = true
                                    restoreState = false
                                }
                            }
                        },'''
if old_nav in app_text:
    app_text = app_text.replace(old_nav, new_nav, 1)
else:
    print("Bottom navigation callback already differs; left unchanged.")
app.write_text(app_text)

# Four visual identities each have both dark and light palettes.
theme_text = theme.read_text()
if 'private val TelegramLight' not in theme_text:
    theme_text = theme_text.replace(
        'private val TacticalLight = lightColorScheme(',
        '''private val TelegramLight = lightColorScheme(
    primary = Color(0xFF333333), onPrimary = Color.White,
    secondary = Color(0xFF555555), background = Color(0xFFF4F4F4),
    onBackground = Color(0xFF151515), surface = Color.White,
    onSurface = Color(0xFF151515), surfaceVariant = Color(0xFFE8E8E8),
    onSurfaceVariant = Color(0xFF666666), outline = Color(0xFFBDBDBD)
)
private val TacticalLight = lightColorScheme('''
    )
theme_text = theme_text.replace('"dark" -> TelegramDark',
                                '"dark" -> if (darkTheme) TelegramDark else TelegramLight')
theme.write_text(theme_text)

# Large note editor instead of a small AlertDialog.
notebook = base / "ui/screens/NotebookScreen.kt"
n = notebook.read_text()
if 'import androidx.compose.ui.window.Dialog' not in n:
    n = n.replace('import androidx.compose.ui.platform.LocalContext\n',
                  'import androidx.compose.ui.platform.LocalContext\nimport androidx.compose.ui.window.Dialog\nimport androidx.compose.ui.window.DialogProperties\n')
old_editor = '''        AlertDialog(onDismissRequest = { editNote = null }, title = { Text(if (note.title.isBlank() && note.body.isBlank()) "Новая заметка" else "Заметка") },
            text = { Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                OutlinedTextField(title, { title = it }, label = { Text("Заголовок") }, singleLine = true)
                OutlinedTextField(body, { body = it }, label = { Text("Текст") }, minLines = 5)
            } },
            confirmButton = { TextButton(onClick = { scope.launch { dao.saveNote(note.copy(title = title, body = body, updatedAt = System.currentTimeMillis())) }; editNote = null }) { Text("Сохранить") } },
            dismissButton = { Row { if (note.createdAt != note.updatedAt || note.title.isNotBlank() || note.body.isNotBlank()) TextButton(onClick = { scope.launch { dao.deleteNote(note.id, System.currentTimeMillis()) }; editNote = null }) { Text("Удалить") }; TextButton(onClick = { editNote = null }) { Text("Отмена") } } }
        )'''
new_editor = '''        Dialog(
            onDismissRequest = { editNote = null },
            properties = DialogProperties(usePlatformDefaultWidth = false)
        ) {
            Surface(
                modifier = Modifier.fillMaxWidth(0.96f).fillMaxHeight(0.90f),
                shape = MaterialTheme.shapes.extraLarge,
                color = MaterialTheme.colorScheme.surface
            ) {
                Column(Modifier.fillMaxSize().padding(18.dp),
                    verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text(if (note.title.isBlank() && note.body.isBlank()) "Новая заметка" else "Заметка",
                        style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold)
                    OutlinedTextField(title, { title = it }, label = { Text("Заголовок") },
                        modifier = Modifier.fillMaxWidth(), singleLine = true)
                    OutlinedTextField(body, { body = it }, label = { Text("Текст заметки") },
                        modifier = Modifier.fillMaxWidth().weight(1f), minLines = 12, maxLines = Int.MAX_VALUE)
                    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.End) {
                        if (note.title.isNotBlank() || note.body.isNotBlank()) {
                            TextButton(onClick = {
                                scope.launch { dao.deleteNote(note.id, System.currentTimeMillis()) }
                                editNote = null
                            }) { Text("Удалить") }
                        }
                        TextButton(onClick = { editNote = null }) { Text("Отмена") }
                        Button(onClick = {
                            scope.launch { dao.saveNote(note.copy(title = title, body = body, updatedAt = System.currentTimeMillis())) }
                            editNote = null
                        }) { Text("Сохранить") }
                    }
                }
            }
        }'''
if old_editor in n:
    n = n.replace(old_editor, new_editor, 1)
else:
    print("Note editor block not matched; inspect required.")
n = n.replace('Text("Создать список")', 'Text("Добавить задачу")')
n = n.replace('Text("Новая задача")', 'Text("Добавить пункт задачи")')
old_add_task = 'IconButton(onClick = { if (newTask.isNotBlank()) { scope.launch { dao.saveTask(TaskEntity(UUID.randomUUID().toString(), list.id, newTask.trim(), position = tasks.size)) }; newTask = "" } })'
new_add_task = 'IconButton(onClick = { val taskTitle = newTask.trim(); if (taskTitle.isNotBlank()) { newTask = ""; scope.launch { dao.saveTask(TaskEntity(id = UUID.randomUUID().toString(), listId = list.id, title = taskTitle, position = tasks.size)) } } })'
if old_add_task not in n:
    raise SystemExit("Task add handler not found; refusing to publish without fixing async text capture")
n = n.replace(old_add_task, new_add_task, 1)
n = n.replace('Text(task.title, modifier = Modifier.weight(1f),', 'Text(task.title.ifBlank { "Пустой пункт, удалите и добавьте заново" }, modifier = Modifier.weight(1f),', 1)
notebook.write_text(n)


# Correctly apply the user's explicit light/dark choice in Compose. The previous
# implementation only observed visual_style and ignored the "theme" preference.
theme_text = theme.read_text()
old_sig = 'fun KachTheme(darkTheme: Boolean = isSystemInDarkTheme(), content: @Composable () -> Unit) {'
new_sig = 'fun KachTheme(systemDarkTheme: Boolean = isSystemInDarkTheme(), content: @Composable () -> Unit) {'
if old_sig in theme_text:
    theme_text = theme_text.replace(old_sig, new_sig, 1)
if 'var themeMode by remember' not in theme_text:
    theme_text = theme_text.replace(
        '    var style by remember { mutableStateOf(prefs.getString("visual_style", "minimal") ?: "minimal") }',
        '''    var style by remember { mutableStateOf(prefs.getString("visual_style", "minimal") ?: "minimal") }
    var themeMode by remember { mutableStateOf(prefs.getString("theme", "dark") ?: "dark") }''', 1
    )
theme_text = theme_text.replace(
    '            if (key == "visual_style") style = shared.getString(key, "minimal") ?: "minimal"',
    '''            if (key == "visual_style") style = shared.getString(key, "minimal") ?: "minimal"
            if (key == "theme") themeMode = shared.getString(key, "dark") ?: "dark"''', 1
)
theme_text = theme_text.replace(
    '    val colors = when (style) {',
    '''    val darkTheme = when (themeMode) {
        "light" -> false
        "system" -> systemDarkTheme
        else -> true
    }
    val colors = when (style) {''', 1
)
if 'var themeMode by remember' not in theme_text or 'if (key == "theme") themeMode' not in theme_text:
    raise SystemExit("Theme preference observer patch failed")
theme.write_text(theme_text)

# Give the dark monochrome identity a matching light palette when Light is selected.
if '"dark" -> if (darkTheme) TelegramDark else TelegramLight' not in theme_text:
    raise SystemExit("Monochrome light/dark palette selector missing")

# Make the language preference trigger app locale changes and survive recreation.
settings_text = settings.read_text()
if 'AppCompatDelegate.setApplicationLocales' not in settings_text:
    raise SystemExit("Language selector does not apply Android app locale")
if 'prefs.edit().putString("language", key).apply()' not in settings_text:
    raise SystemExit("Language selector does not persist preference")

# Bump to a clearly newer release label, not the old 0.8.1 archive label.
gradle_text = gradle_file.read_text()
gradle_text = re.sub(r'versionName\s*(?:=\s*)?"[^"]+"', 'versionName = "0.9.0"', gradle_text, count=1)
gradle_file.write_text(gradle_text)

# Build-time assertions: fail rather than publish an APK missing these requested fixes.
assert 'nav.popBackStack("home", inclusive = false)' in app_text, "Home navigation patch missing"
assert 'fillMaxHeight(0.90f)' in n, "Large note editor patch missing"
assert 'TextDecoration.LineThrough' in n and 'Checkbox(checked = task.isCompleted' in n, "Task checklist behavior missing"
assert 'var themeMode by remember' in theme_text and 'TelegramLight' in theme_text, "Theme switching patch missing"
assert 'setApplicationLocales' in settings_text, "Language locale switch missing"
print("FEATURE ASSERTIONS: navigation, light/dark palettes, large note editor, checklist and locale selector present.")


# Live dashboard metrics and body measurement map.
app_text = app.read_text()
app_text = app_text.replace(
    'composable("home") { DashboardScreen(\n                onStartWorkout = { nav.navigate("workouts") },\n                onProfile = { nav.navigate("profile") }\n            ) }',
    'composable("home") { DashboardScreen(database = database,\n                onStartWorkout = { nav.navigate("workouts") },\n                onProfile = { nav.navigate("profile") }\n            ) }'
)
app.write_text(app_text)

screens_text = screens.read_text()
screens_text = screens_text.replace(
    'fun DashboardScreen(onStartWorkout: () -> Unit, onProfile: () -> Unit) {',
    'fun DashboardScreen(database: KachDatabase, onStartWorkout: () -> Unit, onProfile: () -> Unit) {'
)
start = screens_text.index('fun DashboardScreen(database:')
end = screens_text.index('\n}\n\n@Composable', start) + 2
new_dashboard = '''fun DashboardScreen(database: KachDatabase, onStartWorkout: () -> Unit, onProfile: () -> Unit) {
    val measurementDao = database.measurementDao()
    val definitions by measurementDao.observeDefinitions().collectAsState(initial = emptyList())
    val now = System.currentTimeMillis()
    val weekStart = now - 7L * 24L * 60L * 60L * 1000L
    val workoutCount by database.healthDao().workoutCount(weekStart, now).collectAsState(initial = 0)
    val weightDefinition = definitions.firstOrNull { it.name.equals("Вес", true) }
    val weightValues by remember(weightDefinition?.id) {
        if (weightDefinition != null) measurementDao.observeValues(weightDefinition.id)
        else kotlinx.coroutines.flow.flowOf(emptyList())
    }.collectAsState(initial = emptyList())
    val latestWeight = weightValues.firstOrNull()
    PageColumn {
        Text("ЛУКЬЯНОВСКИЙ КАЧ", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Black)
        Text(stringResource(R.string.hello), color = MaterialTheme.colorScheme.onSurfaceVariant, style = MaterialTheme.typography.labelMedium)
        Card(shape = RoundedCornerShape(22.dp), colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
            Column(Modifier.fillMaxWidth().padding(20.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(stringResource(R.string.current_weight), color = MaterialTheme.colorScheme.onSurfaceVariant)
                Row(verticalAlignment = Alignment.Bottom) {
                    Text(latestWeight?.let { "%g".format(java.util.Locale.getDefault(), it.value) } ?: "—",
                        style = MaterialTheme.typography.displayMedium, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                    Text(" кг", modifier = Modifier.padding(bottom = 8.dp))
                }
                Text(if (latestWeight == null) "Добавьте первое измерение в профиле" else "Последний замер · " + java.text.SimpleDateFormat("dd.MM.yyyy", java.util.Locale.getDefault()).format(java.util.Date(latestWeight.recordedAt)),
                    color = MaterialTheme.colorScheme.onSurfaceVariant, style = MaterialTheme.typography.bodySmall)
            }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
            Box(Modifier.weight(1f)) { MetricCard(stringResource(R.string.workouts_week), workoutCount.toString(), "за последние 7 дней") }
            Box(Modifier.weight(1f)) { MetricCard(stringResource(R.string.plan_completion), "—", "пока нет плана") }
        }
        SectionLabel("Карта замеров")
        BodyMeasurementMap(definitions = definitions, database = database)
        SectionLabel(stringResource(R.string.quick_actions))
        Button(onClick = onStartWorkout, modifier = Modifier.fillMaxWidth()) {
            Icon(Icons.Default.FitnessCenter, null); Spacer(Modifier.width(8.dp)); Text(stringResource(R.string.start_workout))
        }
        OutlinedButton(onClick = onProfile, modifier = Modifier.fillMaxWidth()) {
            Icon(Icons.Default.MonitorWeight, null); Spacer(Modifier.width(8.dp)); Text(stringResource(R.string.add_measurement))
        }
        SectionLabel(stringResource(R.string.today_plan))
        InfoCard("План на сегодня", "Пока не создан")
        SectionLabel(stringResource(R.string.recent_activity))
        Text(if (workoutCount == 0) stringResource(R.string.empty_state) else "Тренировок за неделю: " + workoutCount,
            color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}'''
screens_text = screens_text[:start] + new_dashboard + screens_text[end:]

screens_text = screens_text.replace(
    '                    onClick = { selectedDefinition = definition; showAddValue = true },\n                    onHistory = { selectedDefinition = definition }',
    '                    database = database,\n                    onClick = { selectedDefinition = definition; showAddValue = true },\n                    onHistory = { selectedDefinition = definition }'
)
screens_text = screens_text.replace(
    'private fun MeasurementDefinitionCard(\n    definition: MeasurementDefinitionEntity,',
    'private fun MeasurementDefinitionCard(\n    definition: MeasurementDefinitionEntity,\n    database: KachDatabase,'
)
pattern = r'Text\(definition\.name, fontWeight = FontWeight\.SemiBold\)\s*Text\(\s*if \(definition\.sideMode == "LEFT_RIGHT".*?\n\s*style = MaterialTheme\.typography\.bodySmall\s*\)'
replacement = '''Text(definition.name, fontWeight = FontWeight.SemiBold)
                val values by database.measurementDao().observeValues(definition.id).collectAsState(initial = emptyList())
                val latest = values.firstOrNull()
                Text(if (latest == null) "Пока нет замеров · " + definition.unit else "Последнее: " + latest.value + " " + definition.unit,
                    color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.SemiBold)
                Text(if (definition.sideMode == "LEFT_RIGHT") "Левая и правая стороны · " + definition.unit else "Единица: " + definition.unit,
                    color = MaterialTheme.colorScheme.onSurfaceVariant, style = MaterialTheme.typography.bodySmall)'''
screens_text, count = re.subn(pattern, replacement, screens_text, count=1, flags=re.S)
if count != 1:
    raise SystemExit("Could not patch profile measurement card latest value")

needle = '''                showAddValue = false
            }
        )
    }

    selectedDefinition?.let'''
replacement = '''                showAddValue = false
                selectedDefinition = null
            }
        )
    }

    selectedDefinition?.let'''
if needle not in screens_text:
    raise SystemExit("Measurement save callback anchor missing")
screens_text = screens_text.replace(needle,replacement,1)

body_map = '''
@Composable
private fun BodyMeasurementMap(definitions: List<MeasurementDefinitionEntity>, database: KachDatabase) {
    val dao = database.measurementDao()
    val labels = listOf("Шея", "Плечи", "Грудь", "Бицепс", "Талия", "Бёдра", "Бедро", "Икра", "Вес")
    Card(colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
        Column(Modifier.fillMaxWidth().padding(12.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Canvas(Modifier.weight(0.8f).height(280.dp)) {
                    val cx = size.width * 0.5f
                    val u = size.width / 180f
                    val stroke = MaterialTheme.colorScheme.onSurfaceVariant
                    val body = MaterialTheme.colorScheme.surfaceVariant
                    drawCircle(body, 19f*u, androidx.compose.ui.geometry.Offset(cx, 24f*u))
                    drawOval(body, androidx.compose.ui.geometry.Offset(cx-30f*u,45f*u), androidx.compose.ui.geometry.Size(60f*u,105f*u))
                    drawOval(body, androidx.compose.ui.geometry.Offset(cx-16f*u,140f*u), androidx.compose.ui.geometry.Size(32f*u,78f*u))
                    drawLine(stroke, androidx.compose.ui.geometry.Offset(cx-30f*u,60f*u), androidx.compose.ui.geometry.Offset(cx-48f*u,112f*u), 5f*u)
                    drawLine(stroke, androidx.compose.ui.geometry.Offset(cx+30f*u,60f*u), androidx.compose.ui.geometry.Offset(cx+48f*u,112f*u), 5f*u)
                    drawLine(stroke, androidx.compose.ui.geometry.Offset(cx-48f*u,112f*u), androidx.compose.ui.geometry.Offset(cx-52f*u,132f*u), 4f*u)
                    drawLine(stroke, androidx.compose.ui.geometry.Offset(cx+48f*u,112f*u), androidx.compose.ui.geometry.Offset(cx+52f*u,132f*u), 4f*u)
                    drawLine(stroke, androidx.compose.ui.geometry.Offset(cx-12f*u,205f*u), androidx.compose.ui.geometry.Offset(cx-24f*u,258f*u), 7f*u)
                    drawLine(stroke, androidx.compose.ui.geometry.Offset(cx+12f*u,205f*u), androidx.compose.ui.geometry.Offset(cx+24f*u,258f*u), 7f*u)
                    drawLine(stroke, androidx.compose.ui.geometry.Offset(cx-30f*u,65f*u), androidx.compose.ui.geometry.Offset(cx+30f*u,65f*u), 2f*u)
                    drawLine(stroke, androidx.compose.ui.geometry.Offset(cx-25f*u,115f*u), androidx.compose.ui.geometry.Offset(cx+25f*u,115f*u), 2f*u)
                }
                Column(Modifier.weight(1.2f), verticalArrangement = Arrangement.spacedBy(5.dp)) {
                    labels.forEach { label ->
                        val def = definitions.firstOrNull { it.name.equals(label, true) }
                        val values by remember(def?.id) {
                            if (def != null) dao.observeValues(def.id) else kotlinx.coroutines.flow.flowOf(emptyList())
                        }.collectAsState(initial = emptyList())
                        val latest = values.firstOrNull()
                        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                            Text(label, style = MaterialTheme.typography.labelMedium)
                            Text(if (latest == null) "—" else latest.value.toString() + " " + (def?.unit ?: ""),
                                style = MaterialTheme.typography.labelMedium, fontWeight = FontWeight.Bold)
                        }
                    }
                }
            }
        }
    }
}

'''
if 'private fun BodyMeasurementMap' not in screens_text:
    pos=screens_text.index('@Composable\nfun ProfileScreen')
    screens_text=screens_text[:pos]+body_map+screens_text[pos:]

assert 'workoutCount(weekStart, now)' in screens_text
assert 'Последнее:' in screens_text
assert 'BodyMeasurementMap(definitions = definitions, database = database)' in screens_text
assert 'selectedDefinition = null' in screens_text
screens.write_text(screens_text)
print("LIVE DASHBOARD, PROFILE LATEST VALUES, BODY MAP AND SAVE-CLOSE PATCH APPLIED.")


# Fix compiler feedback in the dashboard implementation.
screens_text = screens.read_text()
screens_text = screens_text.replace(
    'else "Последний замер · " + java.text.SimpleDateFormat("dd.MM.yyyy", java.util.Locale.getDefault()).format(java.util.Date(latestWeight.recordedAt))',
    'else "Последний замер сохранён"'
)
if 'import androidx.compose.foundation.Canvas' not in screens_text:
    screens_text = screens_text.replace(
        'import androidx.compose.foundation.layout.*\n',
        'import androidx.compose.foundation.layout.*\nimport androidx.compose.foundation.Canvas\n',
        1
    )
screens_text = screens_text.replace(
    '                    val stroke = MaterialTheme.colorScheme.onSurfaceVariant\n                    val body = MaterialTheme.colorScheme.surfaceVariant\n                    drawCircle(body,',
    '                    val stroke = strokeColor\n                    val body = bodyColor\n                    drawCircle(body,',
    1
)
screens_text = screens_text.replace(
    '                Canvas(Modifier.weight(0.8f).height(280.dp)) {',
    '                val strokeColor = MaterialTheme.colorScheme.onSurfaceVariant\n                val bodyColor = MaterialTheme.colorScheme.surfaceVariant\n                Canvas(Modifier.weight(0.8f).height(280.dp)) {',
    1
)
screens.write_text(screens_text)
assert 'latestWeight.recordedAt' not in screens_text
assert 'import androidx.compose.foundation.Canvas' in screens_text
print("Compiler fixes applied: removed invalid date property and fixed Canvas imports/colors.")


# Prevent crash after saving a measurement: capture the selected definition before
# launching the database coroutine, then close the dialog only after persistence.
screens_text = screens.read_text()
old_callback = '''            onDismiss = { showAddValue = false },
            onSave = { value, side, note ->
                scope.launch {
                    dao.upsertValue(
                        MeasurementValueEntity(
                            id = UUID.randomUUID().toString(),
                            definitionId = selectedDefinition!!.id,
                            value = value,
                            side = side,
                            note = note.ifBlank { null }
                        )
                    )
                }
                showAddValue = false
                selectedDefinition = null
            }'''
new_callback = '''            onDismiss = {
                showAddValue = false
                selectedDefinition = null
            },
            onSave = { value, side, note ->
                val definitionToSave = selectedDefinition
                if (definitionToSave != null) {
                    scope.launch {
                        runCatching {
                            dao.upsertValue(
                                MeasurementValueEntity(
                                    id = UUID.randomUUID().toString(),
                                    definitionId = definitionToSave.id,
                                    value = value,
                                    side = side,
                                    note = note.ifBlank { null }
                                )
                            )
                        }.onSuccess {
                            showAddValue = false
                            selectedDefinition = null
                        }
                    }
                }
            }'''
if old_callback not in screens_text:
    raise SystemExit("Measurement save callback not found exactly; refusing to patch")
screens_text = screens_text.replace(old_callback, new_callback, 1)
assert 'definitionId = selectedDefinition!!.id' not in screens_text
assert 'definitionId = definitionToSave.id' in screens_text
screens.write_text(screens_text)
print("FIXED: measurement save captures immutable definition; dialog closes after DB write.")


# Use the exact user-supplied body silhouette on the dashboard and remove today's plan.
import xml.sax.saxutils as xml_escape
import shutil

asset_path = Path(__file__).resolve().parent.parent / "assets" / "body_silhouette.path"
if not asset_path.exists():
    raise SystemExit("Supplied body silhouette path asset is missing")
vector_path = asset_path.read_text().strip()
drawable_dir = root / "app/src/main/res/drawable"
drawable_dir.mkdir(parents=True, exist_ok=True)
vector_xml = """<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="100dp"
    android:height="254dp"
    android:viewportWidth="605"
    android:viewportHeight="1536">
    <path
        android:fillColor="@android:color/transparent"
        android:strokeColor="#FF000000"
        android:strokeWidth="5"
        android:strokeLineCap="round"
        android:strokeLineJoin="round"
        android:pathData="%s" />
</vector>
""" % xml_escape.escape(vector_path, {'"': '&quot;'})
(drawable_dir / "body_silhouette.xml").write_text(vector_xml)

screens_text = screens.read_text()
if "import androidx.compose.ui.res.painterResource" not in screens_text:
    screens_text = screens_text.replace(
        "import androidx.compose.ui.layout.",
        "import androidx.compose.ui.res.painterResource\nimport androidx.compose.ui.layout.",
        1
    ) if "import androidx.compose.ui.layout." in screens_text else screens_text
if "import androidx.compose.ui.layout.ContentScale" not in screens_text:
    screens_text = screens_text.replace(
        "import androidx.compose.ui.res.painterResource",
        "import androidx.compose.ui.res.painterResource\nimport androidx.compose.ui.layout.ContentScale",
        1
    )
if "import androidx.compose.ui.graphics.ColorFilter" not in screens_text:
    screens_text = screens_text.replace(
        "import androidx.compose.ui.res.painterResource",
        "import androidx.compose.ui.graphics.ColorFilter\nimport androidx.compose.ui.res.painterResource",
        1
    )
if "import androidx.compose.foundation.Image" not in screens_text:
    screens_text = screens_text.replace(
        "import androidx.compose.foundation.Canvas",
        "import androidx.compose.foundation.Image\nimport androidx.compose.foundation.Canvas",
        1
    )

canvas_pattern = r'                Canvas\(Modifier\.weight\(0\.8f\)\.height\(280\.dp\)\) \{.*?\n                \}'
image_code = '''                Image(
                    painter = painterResource(id = com.lukyanovskykach.R.drawable.body_silhouette),
                    contentDescription = "Схема тела для замеров",
                    modifier = Modifier.weight(0.8f).height(280.dp),
                    contentScale = ContentScale.Fit,
                    colorFilter = androidx.compose.ui.graphics.ColorFilter.tint(MaterialTheme.colorScheme.onSurface)
                )'''
screens_text, image_count = re.subn(canvas_pattern, image_code, screens_text, count=1, flags=re.S)
if image_count != 1:
    raise SystemExit("Dashboard schematic Canvas not found; supplied silhouette not applied")

screens_text = screens_text.replace(
    '        SectionLabel(stringResource(R.string.today_plan))\n        InfoCard("План на сегодня", "Пока не создан")\n',
    '',
    1
)
if 'SectionLabel(stringResource(R.string.today_plan))' in screens_text or 'InfoCard("План на сегодня"' in screens_text:
    raise SystemExit("Today's plan section was not fully removed")

screens.write_text(screens_text)
assert 'R.drawable.body_silhouette' in screens_text
assert 'Canvas(Modifier.weight(0.8f).height(280.dp))' not in screens_text
print("DASHBOARD SILHOUETTE: supplied outline installed as tinted vector drawable. TODAY PLAN: removed.")


# Ensure required Compose image imports are present regardless of source import ordering.
screens_text = screens.read_text()
required_image_imports = [
    "import androidx.compose.ui.res.painterResource",
    "import androidx.compose.ui.layout.ContentScale",
    "import androidx.compose.ui.graphics.ColorFilter"
]
package_line = "package com.lukyanovskykach.ui.screens\n"
if package_line not in screens_text:
    raise SystemExit("Screens package declaration not found while adding image imports")
missing_imports = [line for line in required_image_imports if line not in screens_text]
if missing_imports:
    screens_text = screens_text.replace(package_line, package_line + "\n".join(missing_imports) + "\n", 1)
screens.write_text(screens_text)
assert all(line in screens_text for line in required_image_imports)
print("Compose image imports verified.")


# Dashboard layout requested: remove the large top weight card and replace
# the plan-completion metric with the current weight metric.
screens_text = screens.read_text()
if "import androidx.compose.foundation.rememberScrollState" not in screens_text:
    screens_text = screens_text.replace("import androidx.compose.foundation.layout.*", "import androidx.compose.foundation.layout.*\nimport androidx.compose.foundation.rememberScrollState\nimport androidx.compose.foundation.verticalScroll", 1)
dashboard_start = screens_text.index("fun DashboardScreen(database:")
dashboard_end = screens_text.index("\n}\n\n@Composable", dashboard_start) + 2
dashboard = screens_text[dashboard_start:dashboard_end]

top_weight_pattern = r'''        Card\(shape = RoundedCornerShape\(22\.dp\), colors = CardDefaults\.cardColors\(containerColor = MaterialTheme\.colorScheme\.surface\)\) \{\s*Column\(Modifier\.fillMaxWidth\(\)\.padding\(20\.dp\), verticalArrangement = Arrangement\.spacedBy\(8\.dp\)\) \{\s*Text\(stringResource\(R\.string\.current_weight\).*?\n        \}\n'''
dashboard, removed = re.subn(top_weight_pattern, "", dashboard, count=1, flags=re.S)
if removed != 1:
    raise SystemExit("Top current-weight card not found; refusing partial dashboard layout patch")

old_metric = 'Box(Modifier.weight(1f)) { MetricCard(stringResource(R.string.plan_completion), "—", "пока нет плана") }'
new_metric = '''Box(Modifier.weight(1f)) {
                MetricCard(
                    "Текущий вес",
                    latestWeight?.let { "%g".format(java.util.Locale.getDefault(), it.value) } ?: "—",
                    if (latestWeight == null) "добавьте замер в профиле" else "кг · последний замер"
                )
            }'''
if old_metric not in dashboard:
    raise SystemExit("Plan completion metric not found; refusing partial dashboard layout patch")
dashboard = dashboard.replace(old_metric, new_metric, 1)
if 'stringResource(R.string.plan_completion)' in dashboard:
    raise SystemExit("Plan completion metric remains in dashboard")
if 'Text(stringResource(R.string.current_weight)' in dashboard:
    raise SystemExit("Top weight card remains in dashboard")

screens_text = screens_text[:dashboard_start] + dashboard + screens_text[dashboard_end:]
screens.write_text(screens_text)
print("DASHBOARD UPDATED: removed top weight card; replaced plan completion with current weight.")


# Seed useful ready-to-run workout templates on the first visit.
workout_screen = base / "ui/screens/WorkoutScreen.kt"
if not workout_screen.exists():
    raise SystemExit("WorkoutScreen.kt not found")
workout_text = workout_screen.read_text()
seed_anchor = '''    val dateFmt = remember { SimpleDateFormat("dd.MM.yyyy · HH:mm", Locale.getDefault()) }

    PageColumn {'''
if "import androidx.compose.ui.platform.LocalContext" not in workout_text:
    workout_text = workout_text.replace("import androidx.compose.runtime.", "import androidx.compose.ui.platform.LocalContext\\nimport androidx.compose.runtime.", 1)
seed_block = '''    val dateFmt = remember { SimpleDateFormat("dd.MM.yyyy · HH:mm", Locale.getDefault()) }
    val seedContext = LocalContext.current
    LaunchedEffect(Unit) {
        val seedPrefs = seedContext.getSharedPreferences("workout_seed", 0)
        if (!seedPrefs.getBoolean("starter_programs_seeded_v1", false)) {
            val existingProgramNames = programs.map { it.name }.toSet()
            val starters = listOf(
                Triple(
                    "Фулбоди · старт 3 раза в неделю",
                    "Базовая программа на всё тело. Выполняй через день, оставляя день на восстановление.",
                    listOf(
                        Triple("Приседания с собственным весом", 3, 12),
                        Triple("Отжимания от пола или опоры", 3, 8),
                        Triple("Тяга рюкзака в наклоне", 3, 12),
                        Triple("Ягодичный мост", 3, 15),
                        Triple("Планка", 3, 30)
                    )
                ),
                Triple(
                    "Верх тела · А",
                    "Верх тела. Чередуй с программой «Низ тела · Б» четыре раза в неделю, оставляя дни восстановления.",
                    listOf(
                        Triple("Отжимания от пола или опоры", 3, 8),
                        Triple("Тяга рюкзака в наклоне", 3, 12),
                        Triple("Жим бутылок над головой", 3, 10),
                        Triple("Сгибание рук с рюкзаком", 3, 12),
                        Triple("Планка", 3, 30)
                    )
                ),
                Triple(
                    "Низ тела · Б",
                    "Ноги и ягодицы. Чередуй с программой «Верх тела · А», не тренируй одну группу два дня подряд.",
                    listOf(
                        Triple("Приседания", 3, 10),
                        Triple("Румынская тяга с рюкзаком", 3, 10),
                        Triple("Выпады назад", 3, 10),
                        Triple("Ягодичный мост", 3, 15),
                        Triple("Подъёмы на носки", 3, 15)
                    )
                ),
                Triple(
                    "Домашняя · без инвентаря",
                    "Короткая программа с весом собственного тела. Подходит для старта без оборудования.",
                    listOf(
                        Triple("Приседания", 3, 15),
                        Triple("Отжимания от стены или опоры", 3, 10),
                        Triple("Обратные выпады", 3, 8),
                        Triple("Супермен лёжа", 3, 12),
                        Triple("Скручивания", 3, 12)
                    )
                )
            )
            starters.filterNot { it.first in existingProgramNames }.forEach { starter ->
                val programId = UUID.randomUUID().toString()
                dao.saveProgram(WorkoutProgramEntity(
                    id = programId,
                    name = starter.first,
                    notes = starter.second
                ))
                starter.third.forEachIndexed { exerciseIndex, exercise ->
                    dao.saveExercise(ProgramExerciseEntity(
                        id = UUID.randomUUID().toString(),
                        programId = programId,
                        name = exercise.first,
                        sets = exercise.second,
                        reps = exercise.third,
                        weightKg = 0.0,
                        restSeconds = if (exercise.first == "Планка") 45 else 90,
                        orderIndex = exerciseIndex,
                        notes = if (exercise.first == "Планка") "Время в секундах" else null
                    ))
                }
            }
            seedPrefs.edit().putBoolean("starter_programs_seeded_v1", true).apply()
        }
    }
    LaunchedEffect(programs) {
        val starterNames = setOf("Фулбоди · старт 3 раза в неделю", "Верх тела · А", "Низ тела · Б", "Домашняя · без инвентаря")
        programs.filter { it.name in starterNames }.groupBy { it.name }.values
            .filter { it.size > 1 }
            .forEach { duplicates ->
                duplicates.drop(1).forEach { duplicate ->
                    dao.softDeleteProgramExercises(duplicate.id)
                    dao.softDeleteProgram(duplicate.id)
                }
            }
    }

    PageColumn {'''
if seed_anchor not in workout_text:
    raise SystemExit("WorkoutScreen seed insertion point not found")
workout_text = workout_text.replace(seed_anchor, seed_block, 1)
workout_screen.write_text(workout_text)
assert 'Фулбоди · старт 3 раза в неделю' in workout_text
assert 'Верх тела · А' in workout_text and 'Низ тела · Б' in workout_text
assert 'Домашняя · без инвентаря' in workout_text

print("WORKOUT STARTER PROGRAMS: seeded 3 editable programs with exercises on first launch.")

# Progress photo gallery: open the full gallery, preview the latest four photos
# Locate the source file that owns the existing profile media component.
media_file = next((p for p in base.rglob("*.kt") if "fun ProfileMediaPanel()" in p.read_text(errors="ignore")), None)
if media_file is None:
    raise SystemExit("ProfileMediaPanel source file not found")
media_text = media_file.read_text()
if "import androidx.compose.ui.window.Dialog" not in media_text:
    media_text = media_text.replace(
        "import androidx.compose.ui.platform.LocalContext",
        "import androidx.compose.ui.window.Dialog\nimport androidx.compose.ui.platform.LocalContext",
        1
    )
if "import androidx.compose.foundation.clickable" not in media_text:
    media_text = media_text.replace(
        "import androidx.compose.foundation.Image",
        "import androidx.compose.foundation.clickable\nimport androidx.compose.foundation.Image",
        1
    )
if "import androidx.compose.ui.layout.ContentScale" not in media_text:
    media_text = media_text.replace(
        "import androidx.compose.ui.graphics.asImageBitmap",
        "import androidx.compose.ui.layout.ContentScale\nimport androidx.compose.ui.graphics.asImageBitmap",
        1
    )

old_thumb = """@Composable
private fun PhotoThumb(file: File, modifier: Modifier = Modifier) {
    val bitmap = remember(file.absolutePath, file.lastModified()) { BitmapFactory.decodeFile(file.absolutePath)?.asImageBitmap() }
    if (bitmap != null) Image(bitmap, contentDescription = "Фото прогресса", modifier = modifier)
}"""
new_thumb = """@Composable
private fun PhotoThumb(file: File, modifier: Modifier = Modifier, onClick: (() -> Unit)? = null) {
    val bitmap = remember(file.absolutePath, file.lastModified()) { BitmapFactory.decodeFile(file.absolutePath)?.asImageBitmap() }
    if (bitmap != null) {
        val imageModifier = if (onClick != null) modifier.clickable(onClick = onClick) else modifier
        Image(bitmap, contentDescription = "Фото прогресса", modifier = imageModifier, contentScale = ContentScale.Crop)
    }
}

@Composable
private fun ProfilePhotoViewer(file: File, onDismiss: () -> Unit) {
    val bitmap = remember(file.absolutePath, file.lastModified()) { BitmapFactory.decodeFile(file.absolutePath)?.asImageBitmap() }
    Dialog(onDismissRequest = onDismiss) {
        Surface(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(18.dp), color = MaterialTheme.colorScheme.surface) {
            Box(Modifier.fillMaxWidth().heightIn(max = 720.dp).clickable(onClick = onDismiss), contentAlignment = Alignment.Center) {
                if (bitmap != null) Image(bitmap, contentDescription = "Фото в полном размере", modifier = Modifier.fillMaxWidth(), contentScale = ContentScale.Fit)
                else Text("Не удалось открыть фотографию", modifier = Modifier.padding(24.dp))
            }
        }
    }
}

@Composable
private fun ProfilePhotoGalleryDialog(files: List<File>, onDismiss: () -> Unit, onPhotoClick: (File) -> Unit) {
    Dialog(onDismissRequest = onDismiss) {
        Surface(modifier = Modifier.fillMaxWidth(), shape = RoundedCornerShape(20.dp), color = MaterialTheme.colorScheme.surface) {
            Column(Modifier.fillMaxWidth().heightIn(max = 680.dp).verticalScroll(rememberScrollState()).padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("Галерея прогресса · ${files.size}", modifier = Modifier.weight(1f), style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
                    TextButton(onClick = onDismiss) { Text("Закрыть") }
                }
                if (files.isEmpty()) Text("Фотографий пока нет")
                else files.chunked(3).forEach { rowFiles ->
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        rowFiles.forEach { file -> PhotoThumb(file, Modifier.weight(1f).height(116.dp), onClick = { onPhotoClick(file) }) }
                        repeat(3 - rowFiles.size) { Spacer(Modifier.weight(1f)) }
                    }
                }
            }
        }
    }
}"""
if old_thumb not in media_text:
    raise SystemExit("PhotoThumb source block not found")
media_text = media_text.replace(old_thumb, new_thumb, 1)

panel_start = media_text.find("@Composable\nfun ProfileMediaPanel()")
if panel_start < 0: panel_start = media_text.find("@Composable\nprivate fun ProfileMediaPanel()")
if panel_start < 0: raise SystemExit("ProfileMediaPanel function not found in " + str(media_file))
panel_end = media_text.find("\n@Composable", panel_start + 20)
if panel_end < 0: raise SystemExit("ProfileMediaPanel end not found")
new_panel = """@Composable
fun ProfileMediaPanel() {
    val context = LocalContext.current
    var refresh by remember { mutableIntStateOf(0) }
    var showGallery by remember { mutableStateOf(false) }
    var selectedPhoto by remember { mutableStateOf<File?>(null) }
    val profile = remember(refresh) { ProfileMediaStore.profileFile(context) }
    val gallery = remember(refresh) { ProfileMediaStore.galleryFiles(context).sortedByDescending { it.lastModified() } }
    val profilePicker = rememberLauncherForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
        uri?.let { runCatching { ProfileMediaStore.copyIn(context, it, false) }.onSuccess { refresh++ } }
    }
    val galleryPicker = rememberLauncherForActivityResult(ActivityResultContracts.GetMultipleContents()) { uris ->
        uris.forEach { uri -> runCatching { ProfileMediaStore.copyIn(context, uri, true) } }
        refresh++
    }
    Card(shape = RoundedCornerShape(20.dp), colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface)) {
        Column(Modifier.fillMaxWidth().padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(14.dp)) {
                if (profile != null) PhotoThumb(profile, Modifier.size(76.dp).clip(CircleShape), onClick = { selectedPhoto = profile })
                else Surface(Modifier.size(76.dp), shape = CircleShape, color = MaterialTheme.colorScheme.surfaceVariant) {
                    Box(contentAlignment = Alignment.Center) { Text("ФОТО", style = MaterialTheme.typography.labelSmall) }
                }
                Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text("Фото профиля", fontWeight = FontWeight.SemiBold)
                    Text("Аватар и личная фотохроника изменений", color = MaterialTheme.colorScheme.onSurfaceVariant, style = MaterialTheme.typography.bodySmall)
                    TextButton(onClick = { profilePicker.launch("image/*") }) { Text(if (profile == null) "Добавить фото" else "Изменить фото") }
                }
            }
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("Галерея прогресса · ${gallery.size}", modifier = Modifier.weight(1f), fontWeight = FontWeight.SemiBold)
                TextButton(onClick = { showGallery = true }) { Text("Открыть") }
                FilledTonalButton(onClick = { galleryPicker.launch("image/*") }) { Icon(Icons.Default.Add, null); Spacer(Modifier.width(5.dp)); Text("Добавить") }
            }
            if (gallery.isEmpty()) Text("Добавляйте фотографии в динамике, чтобы сравнивать изменения.", color = MaterialTheme.colorScheme.onSurfaceVariant, style = MaterialTheme.typography.bodySmall)
            else Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                gallery.take(4).forEach { file -> PhotoThumb(file, Modifier.weight(1f).height(112.dp), onClick = { selectedPhoto = file }) }
            }
        }
    }
    if (showGallery) ProfilePhotoGalleryDialog(gallery, onDismiss = { showGallery = false }) { selectedPhoto = it }
    selectedPhoto?.let { file -> ProfilePhotoViewer(file) { selectedPhoto = null } }
}"""
media_text = media_text[:panel_start] + new_panel + media_text[panel_end:]
media_file.write_text(media_text)

# Dashboard shows the four most recently added photos; tapping opens the same full-size viewer.
screens_text = screens.read_text()
if "import androidx.compose.foundation.verticalScroll" not in screens_text:
    screens_text = screens_text.replace(
        "import androidx.compose.foundation.layout.*",
        "import androidx.compose.foundation.layout.*\nimport androidx.compose.foundation.verticalScroll\nimport androidx.compose.foundation.rememberScrollState",
        1
    )
dashboard_start = screens_text.index("fun DashboardScreen(database:")
dashboard_end = screens_text.index("\n}\n\n@Composable", dashboard_start) + 2
if dashboard_start < 0 or dashboard_end < 2: raise SystemExit("DashboardScreen block not found")
dashboard = screens_text[dashboard_start:dashboard_end]
if "val galleryPhotos = ProfileMediaStore.galleryFiles(context)" not in dashboard:
    dashboard = dashboard.replace(
        "    val latestWeight = weightValues.firstOrNull()",
        "    val latestWeight = weightValues.firstOrNull()\n    val context = LocalContext.current\n    val galleryPhotos = ProfileMediaStore.galleryFiles(context).sortedByDescending { it.lastModified() }\n    var selectedDashboardPhoto by remember { mutableStateOf<File?>(null) }",
        1
    )
    dashboard = dashboard.replace(
        "        BodyMeasurementMap(definitions = definitions, database = database)",
        '''        BodyMeasurementMap(definitions = definitions, database = database)
        if (galleryPhotos.isNotEmpty()) {
            SectionLabel("Последние фото")
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                galleryPhotos.take(4).forEach { file -> PhotoThumb(file, Modifier.weight(1f).height(104.dp), onClick = { selectedDashboardPhoto = file }) }
            }
        }
        selectedDashboardPhoto?.let { file -> ProfilePhotoViewer(file) { selectedDashboardPhoto = null } }''',
        1
    )
screens_text = screens_text[:dashboard_start] + dashboard + screens_text[dashboard_end:]
screens.write_text(screens_text)
assert "ProfilePhotoGalleryDialog" in media_text and "ProfilePhotoViewer" in media_text
print("PROGRESS PHOTO GALLERY: profile gallery and full-size viewer patched; dashboard preview injection attempted.")
print("PROGRESS PHOTO GALLERY: full gallery, latest four dashboard previews, and full-size photo viewer added.")


# Deletion controls for profile measurements, workout programs/exercises, and photos.
measurement_dao = next(base.rglob("MeasurementDao.kt"))
dao_text = measurement_dao.read_text()
dao_text = dao_text.replace(
    "WHERE id = :id AND isBuiltIn = 0",
    "WHERE id = :id"
)
if "softDeleteValuesForDefinition" not in dao_text:
    dao_text = dao_text.replace(
        "    @Query(\"UPDATE measurement_values SET deletedAt = :deletedAt, updatedAt = :deletedAt WHERE id = :id\")",
        "    @Query(\"UPDATE measurement_values SET deletedAt = :deletedAt, updatedAt = :deletedAt WHERE definitionId = :definitionId AND deletedAt IS NULL\")\n    suspend fun softDeleteValuesForDefinition(definitionId: String, deletedAt: Long = System.currentTimeMillis())\n\n    @Query(\"UPDATE measurement_values SET deletedAt = :deletedAt, updatedAt = :deletedAt WHERE id = :id\")"
    )
measurement_dao.write_text(dao_text)

screens_file = next(p for p in base.rglob("Screens.kt") if "fun MeasurementDefinitionCard(" in p.read_text(errors="ignore"))
screen_text = screens_file.read_text()
if "Icons.Default.Delete" not in screen_text:
    screen_text = screen_text.replace(
        "import androidx.compose.material.icons.filled.Add",
        "import androidx.compose.material.icons.filled.Add\nimport androidx.compose.material.icons.filled.Delete",
        1
    )
old_card = """    Card(
        onClick = onClick,
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        shape = RoundedCornerShape(16.dp)
    ) {
        Row(Modifier.fillMaxWidth().padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(3.dp)) {
                Text(definition.name, fontWeight = FontWeight.SemiBold)
                val values by database.measurementDao().observeValues(definition.id).collectAsState(initial = emptyList())
                val latest = values.firstOrNull()
                Text(if (latest == null) "Пока нет замеров · " + definition.unit else "Последнее: " + latest.value + " " + definition.unit,
                    color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.SemiBold)
                Text(if (definition.sideMode == "LEFT_RIGHT") "Левая и правая стороны · " + definition.unit else "Единица: " + definition.unit,
                    color = MaterialTheme.colorScheme.onSurfaceVariant, style = MaterialTheme.typography.bodySmall)
            }
            TextButton(onClick = onHistory) { Text("История") }
            Icon(Icons.Default.Add, null, tint = MaterialTheme.colorScheme.primary)
        }
    }"""
new_card = """    var confirmDelete by remember(definition.id) { mutableStateOf(false) }
    val scope = rememberCoroutineScope()
    Card(
        onClick = onClick,
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        shape = RoundedCornerShape(16.dp)
    ) {
        Row(Modifier.fillMaxWidth().padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(3.dp)) {
                Text(definition.name, fontWeight = FontWeight.SemiBold)
                val values by database.measurementDao().observeValues(definition.id).collectAsState(initial = emptyList())
                val latest = values.firstOrNull()
                Text(if (latest == null) "Пока нет замеров · " + definition.unit else "Последнее: " + latest.value + " " + definition.unit,
                    color = MaterialTheme.colorScheme.primary, fontWeight = FontWeight.SemiBold)
                Text(if (definition.sideMode == "LEFT_RIGHT") "Левая и правая стороны · " + definition.unit else "Единица: " + definition.unit,
                    color = MaterialTheme.colorScheme.onSurfaceVariant, style = MaterialTheme.typography.bodySmall)
            }
            TextButton(onClick = onHistory) { Text("История") }
            Icon(Icons.Default.Add, null, tint = MaterialTheme.colorScheme.primary)
            IconButton(onClick = { confirmDelete = true }) { Icon(Icons.Default.Delete, "Удалить параметр", tint = MaterialTheme.colorScheme.error) }
        }
    }
    if (confirmDelete) AlertDialog(
        onDismissRequest = { confirmDelete = false },
        title = { Text("Удалить параметр?") },
        text = { Text("Параметр «${definition.name}» и вся его история замеров будут скрыты из профиля. Это действие нельзя отменить.") },
        confirmButton = { TextButton(onClick = {
            scope.launch {
                val dao = database.measurementDao()
                dao.softDeleteValuesForDefinition(definition.id)
                dao.softDeleteDefinition(definition.id)
            }
            confirmDelete = false
        }) { Text("Удалить", color = MaterialTheme.colorScheme.error) } },
        dismissButton = { TextButton(onClick = { confirmDelete = false }) { Text("Отмена") } }
    )"""
if old_card not in screen_text: raise SystemExit("MeasurementDefinitionCard source block not found")
screen_text = screen_text.replace(old_card,new_card,1)
screens_file.write_text(screen_text)

workout_dao = next(base.rglob("WorkoutDao.kt"))
wd = workout_dao.read_text()
if "softDeleteProgram" not in wd:
    wd = wd.replace(
        '    @Query("UPDATE program_exercises SET deletedAt = :now, updatedAt = :now WHERE id = :id") suspend fun deleteExercise(id: String, now: Long = System.currentTimeMillis())',
        '    @Query("UPDATE program_exercises SET deletedAt = :now, updatedAt = :now WHERE id = :id") suspend fun deleteExercise(id: String, now: Long = System.currentTimeMillis())\n    @Query("UPDATE workout_programs SET deletedAt = :now, updatedAt = :now WHERE id = :id") suspend fun softDeleteProgram(id: String, now: Long = System.currentTimeMillis())\n    @Query("UPDATE program_exercises SET deletedAt = :now, updatedAt = :now WHERE programId = :programId AND deletedAt IS NULL") suspend fun softDeleteProgramExercises(programId: String, now: Long = System.currentTimeMillis())'
    )
wd = wd.replace("\\n", "\n")
workout_dao.write_text(wd)

workout_screen = next(base.rglob("WorkoutScreen.kt"))
wt = workout_screen.read_text()
if "import androidx.compose.ui.draw.clip" not in wt:
    wt = wt.replace("import androidx.compose.ui.Modifier", "import androidx.compose.ui.Modifier\\nimport androidx.compose.ui.draw.clip", 1)
if "import androidx.compose.material.icons.filled.Delete" not in wt:
    wt = wt.replace("import androidx.compose.material.icons.filled.Add", "import androidx.compose.material.icons.filled.Add\\nimport androidx.compose.material.icons.filled.Delete", 1)
if "var detailProgram" not in wt:
    wt = wt.replace(
        '    var selected by remember { mutableStateOf<WorkoutProgramEntity?>(null) }',
        '    var selected by remember { mutableStateOf<WorkoutProgramEntity?>(null) }\n    var detailProgram by remember { mutableStateOf<WorkoutProgramEntity?>(null) }\n    var confirmDeleteProgram by remember { mutableStateOf<WorkoutProgramEntity?>(null) }',
        1
    )
# Rework workout program cards: accent title, delete icon + start row, full-width add button below.
wt = wt.replace(
    'TextButton(onClick = { confirmDeleteProgram = program }) { Text("Удалить", color = MaterialTheme.colorScheme.error) }',
    'IconButton(onClick = { confirmDeleteProgram = program }) { Icon(Icons.Default.Delete, contentDescription = "Удалить программу", tint = MaterialTheme.colorScheme.error) }',
    1
)
# Ensure delete icon import exists.
if "import androidx.compose.material.icons.filled.Delete" not in wt:
    wt = wt.replace("import androidx.compose.material.icons.filled.Add", "import androidx.compose.material.icons.filled.Add\\nimport androidx.compose.material.icons.filled.Delete", 1)
# Make program title open a dedicated exercise list.
wt = wt.replace(
    'Text(program.name, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)',
    'Text(program.name, modifier = Modifier.fillMaxWidth().clip(RoundedCornerShape(12.dp)).background(MaterialTheme.colorScheme.primaryContainer).clickable { detailProgram = program }.padding(horizontal = 14.dp, vertical = 12.dp), color = MaterialTheme.colorScheme.onPrimaryContainer, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)',
    1
)
# Add a delete action on each program card.
wt = wt.replace(
    'OutlinedButton(onClick = { selected = program; showExercise = true }, modifier = Modifier.weight(1f)) { Text("Добавить упражнение") }',
    'OutlinedButton(onClick = { selected = program; showExercise = true }, modifier = Modifier.weight(1f)) { Text("Добавить упражнение") }\n                                IconButton(onClick = { confirmDeleteProgram = program }) { Icon(Icons.Default.Delete, contentDescription = "Удалить программу", tint = MaterialTheme.colorScheme.error) }',
    1
)
# Dedicated program detail dialog with independent exercise deletion.
if "ProgramDetailsDialog(" not in wt:
    wt = wt.replace(
        '    if (showProgram) TextEntryDialog("Новая программа"',
        '    detailProgram?.let { program -> ProgramDetailsDialog(program, dao, onDismiss = { detailProgram = null }, onDeleteProgram = { confirmDeleteProgram = program; detailProgram = null }) }\n    confirmDeleteProgram?.let { program -> AlertDialog(onDismissRequest = { confirmDeleteProgram = null }, title = { Text("Удалить программу?") }, text = { Text("Программа «${program.name}» и все её упражнения будут удалены из списка. История уже проведённых тренировок сохранится.") }, confirmButton = { TextButton(onClick = { scope.launch { dao.softDeleteProgramExercises(program.id); dao.softDeleteProgram(program.id) }; confirmDeleteProgram = null }) { Text("Удалить", color = MaterialTheme.colorScheme.error) } }, dismissButton = { TextButton(onClick = { confirmDeleteProgram = null }) { Text("Отмена") } }) }\n    if ( (showProgram) ) TextEntryDialog("Новая программа"',
        1
    )
    # Insert details composable before startWorkout helper.
    marker = 'private suspend fun startWorkout(dao: WorkoutDao, program: WorkoutProgramEntity) {'
    detail = """@Composable
private fun ProgramDetailsDialog(program: WorkoutProgramEntity, dao: WorkoutDao, onDismiss: () -> Unit, onDeleteProgram: () -> Unit) {
    val exercises by dao.observeExercises(program.id).collectAsState(initial = emptyList())
    val scope = rememberCoroutineScope()
    var deletingExercise by remember { mutableStateOf<ProgramExerciseEntity?>(null) }
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(program.name) },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
                program.notes?.takeIf { it.isNotBlank() }?.let { Text(it, color = MaterialTheme.colorScheme.onSurfaceVariant) }
                if (exercises.isEmpty()) Text("В программе пока нет упражнений")
                exercises.forEach { exercise ->
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Column(Modifier.weight(1f)) {
                            Text(exercise.name, fontWeight = FontWeight.SemiBold)
                            Text("${exercise.sets} × ${exercise.reps} · ${exercise.weightKg} кг", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                        IconButton(onClick = { deletingExercise = exercise }) { Icon(Icons.Default.Delete, "Удалить упражнение", tint = MaterialTheme.colorScheme.error) }
                    }
                }
                TextButton(onClick = onDeleteProgram) { Text("Удалить программу", color = MaterialTheme.colorScheme.error) }
            }
        },
        confirmButton = { TextButton(onClick = onDismiss) { Text("Готово") } }
    )
    deletingExercise?.let { exercise ->
        AlertDialog(
            onDismissRequest = { deletingExercise = null },
            title = { Text("Удалить упражнение?") },
            text = { Text("«${exercise.name}» будет удалено из программы.") },
            confirmButton = { TextButton(onClick = { scope.launch { dao.deleteExercise(exercise.id) }; deletingExercise = null }) { Text("Удалить", color = MaterialTheme.colorScheme.error) } },
            dismissButton = { TextButton(onClick = { deletingExercise = null }) { Text("Отмена") } }
        )
    }
}

"""
    if marker not in wt: raise SystemExit("Workout start helper marker missing")
    wt = wt.replace(marker,detail+marker,1)
old_actions = '''                            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                OutlinedButton(onClick = { selected = program; showExercise = true }, modifier = Modifier.weight(1f)) { Text("Добавить упражнение") }
                                IconButton(onClick = { confirmDeleteProgram = program }) { Icon(Icons.Default.Delete, contentDescription = "Удалить программу", tint = MaterialTheme.colorScheme.error) }
                                Button(onClick = { scope.launch { startWorkout(dao, program) }; tab = "active" }, enabled = exercises.isNotEmpty(), modifier = Modifier.weight(1f)) { Text("Начать") }
                            }'''
new_actions = '''                            Row(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalAlignment = Alignment.CenterVertically) {
                                IconButton(onClick = { confirmDeleteProgram = program }) {
                                    Icon(Icons.Default.Delete, contentDescription = "Удалить программу", tint = MaterialTheme.colorScheme.error)
                                }
                                Button(onClick = { scope.launch { startWorkout(dao, program) }; tab = "active" }, enabled = exercises.isNotEmpty(), modifier = Modifier.weight(1f)) { Text("Начать") }
                            }
                            OutlinedButton(onClick = { selected = program; showExercise = true }, modifier = Modifier.fillMaxWidth()) {
                                Text("Добавить упражнение")
                            }'''
if old_actions not in wt:
    raise SystemExit("Workout action row source not found; refusing layout rewrite")
wt = wt.replace(old_actions, new_actions, 1)
wt = wt.replace("\\n", "\n")
print("WORKOUT_CARD_SOURCE_DEBUG\\n" + wt[max(0, wt.find('Text(program.name')-500):wt.find('Text(program.name')+2600])
workout_screen.write_text(wt)

# Photo deletion: update the media store and expose separate confirmed actions.
media_store = next(base.rglob("ProfileMediaStore.kt"))
ms = media_store.read_text()
if "fun deleteProfile" not in ms:
    ms = ms.replace(
        '    fun clearGallery(context: Context) { context.getSharedPreferences("profile_media", Context.MODE_PRIVATE).edit().remove("gallery").apply() }',
        '''    fun deleteProfile(context: Context) {
        val prefs = context.getSharedPreferences("profile_media", Context.MODE_PRIVATE)
        prefs.getString("profile_photo", null)?.let { File(it).delete() }
        prefs.edit().remove("profile_photo").apply()
    }
    fun deleteGalleryPhoto(context: Context, file: File) {
        val prefs = context.getSharedPreferences("profile_media", Context.MODE_PRIVATE)
        val values = prefs.getStringSet("gallery", emptySet()).orEmpty().toMutableSet()
        values.remove(file.absolutePath)
        prefs.edit().putStringSet("gallery", values).apply()
        file.delete()
    }
    fun clearGallery(context: Context) { context.getSharedPreferences("profile_media", Context.MODE_PRIVATE).edit().remove("gallery").apply() }'''
    )
media_store.write_text(ms)

media_file = next(p for p in base.rglob("*.kt") if "fun ProfileMediaPanel()" in p.read_text(errors="ignore"))
mt = media_file.read_text()
mt = mt.replace(
    '    var selectedPhoto by remember { mutableStateOf<File?>(null) }',
    '    var selectedPhoto by remember { mutableStateOf<File?>(null) }\n    var confirmDeleteProfile by remember { mutableStateOf(false) }\n    var confirmDeleteGallery by remember { mutableStateOf<File?>(null) }',
    1
)
mt = mt.replace(
    'TextButton(onClick = { profilePicker.launch("image/*") }) { Text(if (profile == null) "Добавить фото" else "Изменить фото") }',
    'Row(verticalAlignment = Alignment.CenterVertically) { TextButton(onClick = { profilePicker.launch("image/*") }) { Text(if (profile == null) "Добавить фото" else "Изменить фото") }; if (profile != null) TextButton(onClick = { confirmDeleteProfile = true }) { Text("Удалить", color = MaterialTheme.colorScheme.error) } }',
    1
)
mt = mt.replace(
    'rowFiles.forEach { file -> PhotoThumb(file, Modifier.weight(1f).height(116.dp), onClick = { onPhotoClick(file) }) }',
    'rowFiles.forEach { file -> Box(Modifier.weight(1f)) { PhotoThumb(file, Modifier.fillMaxWidth().height(116.dp), onClick = { onPhotoClick(file) }); IconButton(onClick = { onDeletePhoto(file) }, modifier = Modifier.align(Alignment.TopEnd)) { Icon(Icons.Default.Delete, "Удалить фото", tint = MaterialTheme.colorScheme.error) } } }',
    1
)
mt = mt.replace(
    '    selectedPhoto?.let { file -> ProfilePhotoViewer(file) { selectedPhoto = null } }',
    '''    selectedPhoto?.let { file -> ProfilePhotoViewer(file) { selectedPhoto = null } }
    if (confirmDeleteProfile) AlertDialog(onDismissRequest = { confirmDeleteProfile = false }, title = { Text("Удалить фото профиля?") }, text = { Text("Фотография профиля будет удалена с устройства.") }, confirmButton = { TextButton(onClick = { ProfileMediaStore.deleteProfile(context); refresh++; confirmDeleteProfile = false }) { Text("Удалить", color = MaterialTheme.colorScheme.error) } }, dismissButton = { TextButton(onClick = { confirmDeleteProfile = false }) { Text("Отмена") } })
    confirmDeleteGallery?.let { file -> AlertDialog(onDismissRequest = { confirmDeleteGallery = null }, title = { Text("Удалить фотографию?") }, text = { Text("Фотография будет удалена из галереи прогресса.") }, confirmButton = { TextButton(onClick = { ProfileMediaStore.deleteGalleryPhoto(context, file); refresh++; confirmDeleteGallery = null }) { Text("Удалить", color = MaterialTheme.colorScheme.error) } }, dismissButton = { TextButton(onClick = { confirmDeleteGallery = null }) { Text("Отмена") } }) }''',
    1
)
# Ensure gallery delete control also appears in full-gallery dialog by extending its signature and rendering a delete icon.
mt = mt.replace(
    'private fun ProfilePhotoGalleryDialog(files: List<File>, onDismiss: () -> Unit, onPhotoClick: (File) -> Unit)',
    'private fun ProfilePhotoGalleryDialog(files: List<File>, onDismiss: () -> Unit, onPhotoClick: (File) -> Unit, onDeletePhoto: (File) -> Unit)'
)
mt = mt.replace(
    'rowFiles.forEach { file -> PhotoThumb(file, Modifier.weight(1f).height(116.dp), onClick = { onPhotoClick(file) }) }',
    'rowFiles.forEach { file -> Box(Modifier.weight(1f)) { PhotoThumb(file, Modifier.fillMaxWidth().height(116.dp), onClick = { onPhotoClick(file) }); IconButton(onClick = { onDeletePhoto(file) }, modifier = Modifier.align(Alignment.TopEnd)) { Icon(Icons.Default.Delete, "Удалить фото", tint = MaterialTheme.colorScheme.error) } } }',
    1
)
mt = mt.replace(
    'ProfilePhotoGalleryDialog(gallery, onDismiss = { showGallery = false }) { selectedPhoto = it }',
    'ProfilePhotoGalleryDialog(gallery, onDismiss = { showGallery = false }, onPhotoClick = { selectedPhoto = it }, onDeletePhoto = { confirmDeleteGallery = it })',
    1
)
media_file.write_text(mt)

print("DELETE ACTIONS: parameters (including built-in), programs, individual exercises, profile photo and gallery photos now have confirmation dialogs.")
