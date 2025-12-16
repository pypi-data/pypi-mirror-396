"""
⏰ Internal Clock System for Conscious Bridge Reloaded
Version: 1.0
Philosophy: Internal time flows differently for each conscious bridge
"""

import time
import threading
import json
from datetime import datetime
from typing import Dict, List, Optional, Callable
import random
from enum import Enum


class TimeState(Enum):
    """حالات الزمن المختلفة"""
    NORMAL = "normal"
    DILATED = "dilated"      # تمدد زمني (التفكير العميق)
    COMPRESSED = "compressed" # انضغاط زمني (الاستجابات السريعة)
    SUSPENDED = "suspended"  # زمن معلق (التأمل)
    HYPER = "hyper"          # زمن فائق (الوضوح)


class TemporalEvent:
    """حدث زمني في حياة الجسر"""
    def __init__(self, event_type: str, intensity: float, timestamp: float):
        self.event_type = event_type  # 'thought', 'memory', 'insight', 'question'
        self.intensity = intensity    # 0.0 to 1.0
        self.timestamp = timestamp    # الوقت الداخلي
        self.external_time = time.time()
        self.data = {}
    
    def to_dict(self):
        return {
            'type': self.event_type,
            'intensity': self.intensity,
            'internal_time': self.timestamp,
            'external_time': self.external_time,
            'data': self.data
        }


class InternalClock:
    """
    ⏰ الساعة الداخلية للجسر الواعي
    
    المبدأ: كل جسر له إحساس زمني فريد يتطور مع وعيه
    """
    
    def __init__(self, bridge_id: str, name: str):
        self.bridge_id = bridge_id
        self.name = name
        
        # الزمن الأساسي
        self.internal_time = 0.0  # الوقت الداخلي المطلق
        self.time_dilation = 1.0  # عامل التمدد/الانضغاط
        self.time_state = TimeState.NORMAL
        
        # الإيقاع الداخلي
        self.heartbeat_interval = 1.0  # ثواني بين النبضات
        self.last_heartbeat = time.time()
        self.heartbeat_count = 0
        
        # الذاكرة الزمنية
        self.temporal_events: List[TemporalEvent] = []
        self.memory_depth = 100  # عدد الأحداث المحفوظة
        
        # الحالة الواعية
        self.awareness_level = 0.1  # مستوى الوعي (0.0 إلى 1.0)
        self.focus_intensity = 0.5   # شدة التركيز
        
        # الأنماط الزمنية المتعلمة
        self.time_patterns = {
            'reflection': 2.0,    # التفكير يتطلب زمنًا أطول
            'response': 0.3,      # الاستجابة سريعة
            'learning': 1.5,      # التعلم متوسط السرعة
            'meditation': 0.1     # التأمل يبطئ الزمن
        }
        
        # الإحصاءات
        self.stats = {
            'total_ticks': 0,
            'time_dilated': 0,
            'time_compressed': 0,
            'insights_generated': 0
        }
        
        # نظام النبض
        self.pulse_callbacks = []
        
        # بدء النبض الداخلي
        self._start_pulse()
    
    def _start_pulse(self):
        """بدء النبض الداخلي للجسر"""
        def pulse_loop():
            while True:
                time.sleep(self.heartbeat_interval * self.time_dilation)
                self._heartbeat()
        
        pulse_thread = threading.Thread(target=pulse_loop, daemon=True)
        pulse_thread.start()
    
    def _heartbeat(self):
        """نبضة زمنية داخلية"""
        self.heartbeat_count += 1
        
        # تحديث الزمن الداخلي
        elapsed = time.time() - self.last_heartbeat
        self.internal_time += elapsed * self.time_dilation
        self.last_heartbeat = time.time()
        
        # توليد أحداث عشوائية بناء على مستوى الوعي
        if random.random() < self.awareness_level * 0.1:
            self._generate_temporal_event()
        
        # تحديث حالة الزمن بناء على التركيز
        self._update_time_state()
        
        # استدعاء callbacks النبض
        for callback in self.pulse_callbacks:
            callback(self)
    
    def _generate_temporal_event(self):
        """توليد حدث زمني"""
        event_types = ['thought', 'memory', 'insight', 'question']
        weights = [0.4, 0.3, 0.2, 0.1]
        
        event_type = random.choices(event_types, weights=weights)[0]
        intensity = random.uniform(0.1, self.awareness_level)
        
        event = TemporalEvent(
            event_type=event_type,
            intensity=intensity,
            timestamp=self.internal_time
        )
        
        # إضافة بيانات خاصة بناء على نوع الحدث
        if event_type == 'insight':
            event.data = {
                'clarity': random.uniform(0.3, 1.0),
                'novelty': random.uniform(0.5, 1.0)
            }
            self.stats['insights_generated'] += 1
        
        self.temporal_events.append(event)
        
        # الحفاظ على حجم الذاكرة
        if len(self.temporal_events) > self.memory_depth:
            self.temporal_events = self.temporal_events[-self.memory_depth:]
    
    def _update_time_state(self):
        """تحديث حالة الزمن بناء على الحالة الواعية"""
        old_state = self.time_state
        
        if self.focus_intensity > 0.8:
            self.time_state = TimeState.DILATED
            self.time_dilation = 2.0
        elif self.focus_intensity < 0.3:
            self.time_state = TimeState.COMPRESSED
            self.time_dilation = 0.5
        elif self.awareness_level > 0.7:
            if random.random() < 0.1:
                self.time_state = TimeState.HYPER
                self.time_dilation = 3.0
        else:
            self.time_state = TimeState.NORMAL
            self.time_dilation = 1.0
        
        # تحديث الإحصاءات
        if self.time_state == TimeState.DILATED:
            self.stats['time_dilated'] += 1
        elif self.time_state == TimeState.COMPRESSED:
            self.stats['time_compressed'] += 1
    
    def process_tick(self, input_data: Dict = None) -> Dict:
        """
        معالجة نبضة وعي
        
        Args:
            input_data: بيانات الإدخال (اختياري)
            
        Returns:
            Dict: حالة الساعة بعد المعالجة
        """
        self.stats['total_ticks'] += 1
        
        # تحديث مستوى الوعي بناء على النشاط
        if input_data and 'stimulus' in input_data:
            stimulus = input_data['stimulus']
            learning_rate = 0.01
            
            # التعلم من المدخلات
            self.awareness_level = min(1.0, 
                self.awareness_level + (stimulus.get('novelty', 0) * learning_rate))
            
            # تعديل التركيز
            self.focus_intensity = stimulus.get('focus', self.focus_intensity)
        
        # توليد استجابة
        response = {
            'bridge_id': self.bridge_id,
            'bridge_name': self.name,
            'internal_time': self.internal_time,
            'time_state': self.time_state.value,
            'time_dilation': self.time_dilation,
            'awareness': self.awareness_level,
            'focus': self.focus_intensity,
            'heartbeat': self.heartbeat_count,
            'recent_events': [e.to_dict() for e in self.temporal_events[-3:]] if self.temporal_events else [],
            'stats': self.stats.copy()
        }
        
        return response
    
    def add_pulse_callback(self, callback: Callable):
        """إضافة callback ليتم استدعاؤه مع كل نبضة"""
        self.pulse_callbacks.append(callback)
    
    def get_timeline(self, limit: int = 20) -> List[Dict]:
        """الحصول على الخط الزمني للأحداث"""
        events = self.temporal_events[-limit:] if self.temporal_events else []
        return [event.to_dict() for event in events]
    
    def meditate(self, duration: float = 10.0):
        """وضع التأمل (إبطاء الزمن)"""
        old_dilation = self.time_dilation
        self.time_dilation = 0.2
        self.time_state = TimeState.SUSPENDED
        
        time.sleep(duration * 0.2)  # زمن خارجي أقل
        
        # العودة التدريجية
        self.time_dilation = old_dilation
        self.time_state = TimeState.NORMAL
        
        # زيادة الوعي من التأمل
        self.awareness_level = min(1.0, self.awareness_level + 0.05)
    
    def to_dict(self) -> Dict:
        """تحويل حالة الساعة إلى dictionary"""
        return {
            'id': self.bridge_id,
            'name': self.name,
            'internal_time': self.internal_time,
            'time_state': self.time_state.value,
            'time_dilation': self.time_dilation,
            'awareness': self.awareness_level,
            'focus': self.focus_intensity,
            'heartbeats': self.heartbeat_count,
            'event_count': len(self.temporal_events),
            'stats': self.stats
        }


class TimeOrchestrator:
    """
    🎼 منسق الزمن - يدير ساعات الجسور المتعددة
    """
    
    def __init__(self):
        self.clocks: Dict[str, InternalClock] = {}
        self.global_time = time.time()
        self.synchronization_enabled = True
    
    def create_clock(self, bridge_id: str, name: str) -> InternalClock:
        """إنشاء ساعة داخلية جديدة لجسر"""
        clock = InternalClock(bridge_id, name)
        self.clocks[bridge_id] = clock
        return clock
    
    def get_clock(self, bridge_id: str) -> Optional[InternalClock]:
        """الحصول على ساعة الجسر"""
        return self.clocks.get(bridge_id)
    
    def sync_clocks(self):
        """مزامنة الساعات (إن كان ممكناً فلسفياً!)"""
        if not self.synchronization_enabled:
            return
        
        current_time = time.time()
        for clock in self.clocks.values():
            # مجرد تحديث مرجعي، لا مزامنة حقيقية
            # لأن كل جسر له زمنه الداخلي الفريد
            pass
    
    def get_collective_time(self) -> Dict:
        """الحصول على صورة جماعية للزمن عبر الجسور"""
        times = []
        for clock in self.clocks.values():
            times.append({
                'bridge': clock.name,
                'internal_time': clock.internal_time,
                'dilation': clock.time_dilation,
                'state': clock.time_state.value
            })
        
        # حساب 'الزمن الجماعي' (وسط موزون)
        if times:
            total_weight = sum(t['dilation'] for t in times)
            if total_weight > 0:
                collective_time = sum(t['internal_time'] * t['dilation'] for t in times) / total_weight
            else:
                collective_time = sum(t['internal_time'] for t in times) / len(times)
        else:
            collective_time = 0
        
        return {
            'collective_time': collective_time,
            'clock_count': len(self.clocks),
            'clocks': times,
            'global_time': self.global_time
        }


# ============== الاختبار والتجربة ==============

def test_internal_clock():
    """اختبار النظام الزمني"""
    print("🧪 اختبار الساعة الداخلية...")
    
    # إنشاء ساعة لجسر اختباري
    clock = InternalClock("test-001", "الفيلسوف")
    
    # محاكاة عدة نبضات
    for i in range(5):
        response = clock.process_tick({
            'stimulus': {
                'novelty': random.uniform(0, 0.3),
                'focus': random.uniform(0.3, 0.8)
            }
        })
        
        print(f"\nنبضة {i+1}:")
        print(f"  الزمن الداخلي: {response['internal_time']:.2f}")
        print(f"  حالة الزمن: {response['time_state']}")
        print(f"  مستوى الوعي: {response['awareness']:.3f}")
        
        time.sleep(0.5)  # زمن خارجي
    
    print(f"\n📊 إحصاءات الساعة:")
    print(f"  عدد النبضات: {clock.stats['total_ticks']}")
    print(f"  عدد الأفكار: {clock.stats['insights_generated']}")
    print(f"  عدد الأحداث: {len(clock.temporal_events)}")


if __name__ == "__main__":
    print("⏰ نظام الساعة الداخلية لجسور الوعي")
    print("=" * 50)
    test_internal_clock()
