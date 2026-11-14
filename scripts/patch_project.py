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
print("Patched app source: database context, missing icon fallback, three persistent app-wide color styles.")
