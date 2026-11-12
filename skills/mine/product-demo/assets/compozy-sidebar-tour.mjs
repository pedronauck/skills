// Same flow as the CleanShot reference, plus dragging the drawer divider.
export const options = { size: '1512x982', fps: 60 };

const b = (name) => `role=button[name="${name}"]`;

export default async function (demo) {
  // Reach the starting state through demo.page: none of this is recorded, and no seeded id is hardcoded.
  await demo.goto('/sessions');
  await demo.page.getByRole('button', { name: /Session badge: running Rehearse the queue cutover again/ }).click();
  await demo.waitFor('text=Draining the staging queue');
  // Lab mock notifications are noise in the shot.
  await demo.page.addStyleTag({ content: '[data-sonner-toaster],section[aria-label^="Notifications"]{display:none!important}' });
  await demo.wait(0.3);

  await demo.click(`${b('2 subagents')} >> nth=0`);
  await demo.wait(0.9);

  await demo.focus(b('Infra Drift · platform-infra · Needs you'), { zoom: 2.2, duration: 1.2 });
  await demo.hover(b('Infra Drift · platform-infra · Needs you'));
  await demo.wait(1.1);
  await demo.focus(b('Dependency Watch · platform-infra · Idle'), { zoom: 2.2, duration: 1.2 });
  await demo.hover(b('Dependency Watch · platform-infra · Idle'));
  await demo.wait(1.1);
  await demo.moveTo(b('platform-infra 9'));
  await demo.wait(0.5);

  await demo.click(b('Queue cutover 4'));
  await demo.wait(0.7);
  await demo.click(b('Queue cutover 4'));
  await demo.wait(0.7);

  await demo.click(b('Open Drain the old queue · claude · Opus 5 · Code implementer'));
  await demo.waitFor('text=Drain the old queue: done');
  await demo.wait(0.9);

  await demo.drag('role=separator[name="Resize drawer"]', { x: 800, y: 540 });
  await demo.wait(0.7);
  await demo.drag('role=separator[name="Resize drawer"]', { x: 1180, y: 540 });
  await demo.wait(0.7);

  await demo.click(b('Close drawer'));
  await demo.wait(0.6);

  await demo.hover(b('Command palette'));
  await demo.focus(b('Command palette'), { zoom: 2.4, duration: 1.3 });
  await demo.wait(1.2);
  await demo.wide();
  await demo.wait(1.0);
}
