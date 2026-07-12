import React, { useState, useCallback, useRef, useEffect } from 'react';
import NationSelect from './components/NationSelect.jsx';
import GameScreen from './components/GameScreen.jsx';
import GameOver from './components/GameOver.jsx';
import { createSimulation } from './engine/simulation.js';

export default function App() {
  const [screen, setScreen] = useState('select'); // select | playing | gameover
  const [sim, setSim] = useState(null);
  const [nationId, setNationId] = useState(null);
  const [gameState, setGameState] = useState(null);
  const [pendingTransition, setPendingTransition] = useState(null);
  const [lastTickEvents, setLastTickEvents] = useState([]);
  const [policiesThisTurn, setPoliciesThisTurn] = useState(0);
  const timerRef = useRef(null);

  const startGame = useCallback((nid) => {
    const simulation = createSimulation(nid, Math.floor(Math.random() * 100000));
    setSim(simulation);
    setNationId(nid);
    setGameState({ ...simulation.state });
    setScreen('playing');
    setLastTickEvents([]);
    setPoliciesThisTurn(0);
  }, []);

  const applyPolicy = useCallback((policyId, investment) => {
    if (!sim) return;
    const result = sim.applyPolicy(policyId, investment);
    setPoliciesThisTurn(p => p + 1);
    setGameState({ ...sim.state });
    return result;
  }, [sim]);

  const advanceYear = useCallback(() => {
    if (!sim) return;

    // Check era transition before ticking
    const transition = sim.checkEraTransition();
    if (transition) {
      setPendingTransition(transition);
      setGameState({ ...sim.state });
      return;
    }

    const yearLog = sim.tick();
    setLastTickEvents(yearLog.events);
    setPoliciesThisTurn(0);
    setGameState({ ...sim.state });

    if (sim.isGameOver()) {
      setScreen('gameover');
    }
  }, [sim]);

  const dismissTransition = useCallback(() => {
    setPendingTransition(null);
    const yearLog = sim.tick();
    setLastTickEvents(yearLog.events);
    setPoliciesThisTurn(0);
    setGameState({ ...sim.state });
    if (sim.isGameOver()) {
      setScreen('gameover');
    }
  }, [sim]);

  const restart = useCallback(() => {
    setScreen('select');
    setSim(null);
    setGameState(null);
    setPendingTransition(null);
    setLastTickEvents([]);
    setPoliciesThisTurn(0);
  }, []);

  if (screen === 'select') {
    return <NationSelect onSelect={startGame} />;
  }

  if (screen === 'gameover' && sim) {
    return <GameOver sim={sim} onRestart={restart} />;
  }

  if (screen === 'playing' && gameState) {
    return (
      <GameScreen
        gameState={gameState}
        nationId={nationId}
        policiesThisTurn={policiesThisTurn}
        lastTickEvents={lastTickEvents}
        pendingTransition={pendingTransition}
        onApplyPolicy={applyPolicy}
        onAdvanceYear={advanceYear}
        onDismissTransition={dismissTransition}
        getAvailablePolicies={() => sim.getAvailablePolicies()}
        getEraConfig={() => sim.getEraConfig()}
        getScore={() => sim.getScore()}
        getPhasePosition={() => sim.getPhasePosition()}
      />
    );
  }

  return null;
}
