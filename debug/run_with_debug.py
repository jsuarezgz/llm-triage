# debug/run_with_full_debug.py - VERSIÓN MEJORADA
#!/usr/bin/env python3
"""
Script para ejecutar análisis con debug completo y automático
"""

import sys
import asyncio
import os
from pathlib import Path

# Agregar directorio raíz al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def setup_debug_environment():
    """Configurar entorno para debug completo"""
    
    # Importar y configurar debugger
    from debug.llm_debugger import start_debug_session, get_debugger
    from application.factory import create_debug_factory
    
    print("🔍 Starting FULL CONTENT LLM Debug Session...")
    print("📝 This will log complete requests and responses to debug file")
    
    # Verificar si hay API key
    api_key = os.getenv("RESEARCH_API_KEY")
    if api_key:
        print(f"🔑 API Key detected: {api_key[:8]}***{api_key[-4:]}")
    else:
        print("⚠️  No API key - will use mock responses")
    
    # Iniciar debug session con contenido completo
    start_debug_session(full_content=True)
    
    debugger = get_debugger()
    print(f"📄 Debug file: {debugger.log_file}")
    
    return debugger

def patch_factory_for_debug():
    """Patchear el factory por defecto para usar debug"""
    
    import application.factory as factory_module
    
    # Guardar la función original
    original_create_factory = factory_module.create_factory
    
    # Crear función de reemplazo que habilita debug
    def create_debug_enabled_factory():
        factory = original_create_factory()
        factory.enable_debug_mode()
        return factory
    
    # Reemplazar la función
    factory_module.create_factory = create_debug_enabled_factory
    
    print("🔧 Factory patched to enable debug mode")

def main():
    """Ejecutar CLI con debug completo habilitado automáticamente"""
    
    debugger = None
    
    try:
        # Configurar debug
        debugger = setup_debug_environment()
        
        # Patchear factory para habilitar debug automáticamente
        patch_factory_for_debug()
        
        # Importar CLI después del patch
        from application.cli import cli
        
        print("\n🚀 Starting analysis with full debug logging...")
        print("📡 All LLM clients will be automatically configured for debug")
        
        # Ejecutar CLI normal - ahora con debug automático
        cli()
        
    except SystemExit as e:
        # SystemExit es normal para CLI
        if e.code != 0:
            print(f"⚠️  CLI exited with code: {e.code}")
    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Finalizar debug session
        if debugger:
            print("\n📊 Finalizing debug session...")
            from debug.llm_debugger import end_debug_session
            end_debug_session()
            
            # Mostrar estadísticas finales
            stats = debugger.get_summary_stats()
            print(f"\n✅ Debug session completed!")
            print(f"   📞 Total calls: {stats['total_calls']}")
            print(f"   ⏱️  Total time: {stats['total_time_seconds']:.2f}s")
            print(f"   🔧 LLM clients controlled: {stats['active_llm_clients']}")
            
            if Path(debugger.log_file).exists():
                log_size = Path(debugger.log_file).stat().st_size / 1024 / 1024
                print(f"   📄 Log file size: {log_size:.2f} MB")
                print(f"   📂 Log location: {debugger.log_file}")

if __name__ == '__main__':
    main()
