from typing import Dict, List
from datetime import datetime

from app.core.logger import get_logger

logger = get_logger(__name__)


class AlertManager:
    def __init__(self):
        self.active_alerts = []
        self.alert_history = []

    def _next_id(self) -> int:
        return len(self.alert_history) + 1

    def _store(self, alert: Dict) -> Dict:
        self.active_alerts.append(alert)
        self.alert_history.append(alert)
        severity = alert.get('severity', 'info').upper()
        msg = alert['message']
        if severity == 'CRITICAL':
            logger.critical(f"[ALERT] {msg}")
        elif severity == 'HIGH':
            logger.error(f"[ALERT] {msg}")
        elif severity == 'MEDIUM':
            logger.warning(f"[ALERT] {msg}")
        else:
            logger.info(f"[ALERT] {msg}")
        return alert

    def create_drift_alert(self, user_id, severity, delta, previous_limit, new_limit) -> Dict:
        return self._store({
            'alert_id': self._next_id(), 'type': 'drift', 'user_id': user_id, 'severity': severity,
            'message': f"Credit limit drift for user {user_id}: {previous_limit:.0f} -> {new_limit:.0f} (delta={delta:.0f})",
            'timestamp': datetime.utcnow().isoformat(), 'resolved': False
        })

    def create_fairness_alert(self, cohort1, cohort2, metric_name, gap, threshold) -> Dict:
        return self._store({
            'alert_id': self._next_id(), 'type': 'fairness', 'cohort1': cohort1, 'cohort2': cohort2,
            'metric': metric_name,
            'message': f"Fairness violation: {cohort1} vs {cohort2} on {metric_name} (gap={gap:.0f}, threshold={threshold:.0f})",
            'timestamp': datetime.utcnow().isoformat(), 'resolved': False
        })

    def create_model_alert(self, metric_name, value, threshold) -> Dict:
        return self._store({
            'alert_id': self._next_id(), 'type': 'model_performance', 'metric': metric_name,
            'value': value, 'threshold': threshold,
            'message': f"Model performance: {metric_name}={value:.4f} below threshold {threshold:.4f}",
            'timestamp': datetime.utcnow().isoformat(), 'resolved': False
        })

    def resolve_alert(self, alert_id: int, resolution: str = "") -> bool:
        for alert in self.active_alerts:
            if alert['alert_id'] == alert_id:
                alert.update({'resolved': True, 'resolved_at': datetime.utcnow().isoformat(), 'resolution': resolution})
                self.active_alerts.remove(alert)
                logger.info(f"Alert {alert_id} resolved")
                return True
        return False

    def get_active_alerts(self, alert_type: str = None) -> List[Dict]:
        if alert_type:
            return [a for a in self.active_alerts if a['type'] == alert_type]
        return self.active_alerts

    def get_alert_summary(self) -> Dict:
        types = ['drift', 'fairness', 'model_performance']
        severities = ['critical', 'high', 'medium', 'low']
        return {
            'total_active': len(self.active_alerts),
            'total_history': len(self.alert_history),
            'by_type': {t: sum(1 for a in self.active_alerts if a['type'] == t) for t in types},
            'by_severity': {s: sum(1 for a in self.active_alerts if a.get('severity') == s) for s in severities}
        }


alert_manager = AlertManager()
