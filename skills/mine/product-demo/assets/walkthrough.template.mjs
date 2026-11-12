// Zoom follows the cursor (showtime autozoom). See product-demo SKILL.md "Script rules".
export const options = { size: '1512x982', fps: 60 };

const b = (name) => `role=button[name="${name}"]`;

export default async function (demo) {
  // Not recorded: reach the starting state here, with demo.page if it takes a click.
  await demo.goto('/START_ROUTE');
  await demo.waitFor('text=TEXT_THAT_PROVES_THE_SCREEN_LOADED');
  await demo.wait(0.3);

  await demo.click(b('FIRST_TARGET'));
  await demo.wait(0.9);

  // Camera hint first, then the pointer, so the zoom moves with the cursor.
  await demo.focus(b('HOVER_TARGET'), { zoom: 2.2, duration: 1.2 });
  await demo.hover(b('HOVER_TARGET'));
  await demo.wait(1.1);

  // A popover covers what is under it: park the pointer elsewhere before the next click.
  await demo.moveTo(b('NEUTRAL_TARGET'));
  await demo.wait(0.5);

  await demo.drag('role=separator[name="HANDLE"]', { x: 800, y: 540 });
  await demo.wait(0.7);

  await demo.wide();
  await demo.wait(1.0);
}
